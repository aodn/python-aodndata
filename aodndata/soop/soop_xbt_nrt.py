import datetime
import os
import re
from configparser import ConfigParser

import numpy as np
import pandas as pd
from aodntools.ncwriter import ImosTemplate
from fuzzywuzzy import process as fwprocess
from netCDF4 import date2num, Dataset
from pkg_resources import resource_filename

from aodncore.pipeline import FileType, HandlerBase, PipelineFilePublishType, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileContentError, MissingConfigParameterError
from aodncore.vocab.xbt_line_vocab import XbtLineVocabHelper
from .ship_callsign import ship_callsign_list

BUFR_VAR = ({
    'data': ({
        'depth': 7063,
        'temp': 22043,
        'glob_gtspp': 33050,
        'qual_gtspp': 8080,
    }),
    'date': ({
        'year': 4001,
        'month': 4002,
        'day': 4003,
        'hour': 4004,
        'minute': 4005,
    }),
    'location': ({
        'latitude': 5001,
        'longitude': 6001
    }),
    'metadata': ({
        'XBT_uniqueid': 1079,
        'ship_id': 1011,
        'imo_number': 1103,
        'wmo_id': 1087,
        'ship_name': 1019,
        'XBT_line': 1080,
        'ship_transect_number': 5036,
        'agency_in_charge': 1036,
        'Height_of_XBT_launcher': 22177,
        'XBT_probetype_fallrate_equation': 22067,
        'XBT_height_launch_above_water_in_meters': 22177,
        'speed_of_motion_of_moving_observing_platform': 1013,
        'direction_of_motion_of_moving_observing_platform': 1012,
        'XBT_recorder_type': 22068,
        'software_id': 25061,
        'method_water_temp_and_or_sal_measurement': 2038,
        'depth_below_sea_water_surface': 7063,
        'XBT_instrument_serialnumber': 2171,
        'indicator_for_digitization': 2032,
        'extended_delayed_descriptor_factor': 31002
    }),
})
NC_JSON_TEMPLATE_BUFR = resource_filename("aodndata", "templates/soop_xbt_nrt_bufr_nc_template.json")
XBT_CONFIG = resource_filename("aodndata", "configurations/soop_xbt_config.ini")
KELVIN_TO_CELSIUS = 273.15


class SoopXbtNrtHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopXbtNrtHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.csv']

        try:
            self.xbt_line_vocab_url = self.config.pipeline_config['global']['xbt_line_vocab_url']
        except KeyError:
            raise MissingConfigParameterError(
                "missing required config item 'xbt_line_vocab_url' in the pipeline config"
            )

    def preprocess(self):
        """
        pre processsing to handle the conversion of BUFR csv files to NetCDF
        :return:
        """
        csv_file = self.file_collection.filter_by_attribute_id('file_type', FileType.CSV)

        if csv_file:
            csv_file = csv_file[0]
            csv_file.publish_type = PipelineFilePublishType.ARCHIVE_ONLY

            profiles = parse_bufr_file(csv_file.src_path)
            profiles = return_unique_profiles(profiles)  # check for duplicate profiles within BUFR file
            for profile in profiles:
                profile = fzf_vessel_get_info(profile)  # fuzzy search finder for vessel name
                profile = xbt_line_get_info(profile, self.xbt_line_vocab_url)  # get hard coded info per xbt line
                netcdf_filepath = netcdf_writer(profile, self.temp_dir)  # convert BUFR to NetCDF

                # publish
                nc_file = PipelineFile(netcdf_filepath)
                nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
                self.file_collection.add(nc_file)

    @staticmethod
    def archive_path(filepath):
        """
        dest_path function for a BUFR csv file
        :param filename:
        :return:
        """
        filename = os.path.basename(filepath)
        file_year = str(datetime.datetime.strptime(filename.split('_')[2], '%Y%m%d%H%M%S').year)
        return os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME_BUFR', file_year, filename)

    @staticmethod
    def dest_path(filepath):
        """
        dest_path function for NetCDF file only
        realtime data hierarchy is different from delayed mode hierarchy, keeping as-is:

        * realtime: {xbt_line_code}_{xbt_line_description}
        * delayed: {vessel_callsign}_{vessel_name}

        :param filepath:
        :return: dest_path string
        """

        with Dataset(filepath, mode='r') as nc_obj:
            xbt_callsign = nc_obj.Callsign
            xbt_shipname = nc_obj.ship_name
            year = datetime.datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")
            return os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME',
                                '{xbt_callsign}_{xbt_shipname}'.format(xbt_callsign=xbt_callsign,
                                                                       xbt_shipname=xbt_shipname),
                                year,
                                os.path.basename(filepath))


def return_unique_profiles(profiles):
    """
    Some BUFR files have their profiles being repeated. This is less than ideal. This function returns the non-duplicate
    profiles
    :param profiles: output from the parse_bufr_file function
    :return: list of unique profiles
    """
    unique_ids = []
    profiles_unique = []
    for idx, profile in enumerate(profiles):
        unique_id = profile['profile_metadata']['XBT_uniqueid']
        if unique_id not in unique_ids:
            unique_ids.append(unique_id)
            profiles_unique.append(profile)  # copy unique profiles to new list

    return profiles_unique


def _bufr_to_pd(csv_path):
    """
    read a BUFR CSV file and store into a panda dataframe
    :param csv_path:
    :return: pandas dataframe
    """
    df = pd.read_csv(csv_path, header=None,
                     engine='python',
                     error_bad_lines=False)
    df.columns = ["row", "id", "id_name", "id_value"]
    return df


def parse_bufr_file(csv_path):
    """
    Parse a BUFR file containing 1 or more profiles
    :param csv_path: input BUFR file in csv format
    :return: data array (each array value is a different profile) containing various dictionaries
             keys: 'profile_data', 'profile_geotime', 'profile_metadata'
    """
    df = _bufr_to_pd(csv_path)

    # find all profiles in BUFR file
    idx_profs = df["row"].loc[df["id"] == BUFR_VAR['metadata']['XBT_uniqueid']].index.values.astype(int)

    # initialise for loop values
    n_prof = len(idx_profs)  # number of profile in file
    skip_rows = 56  # number of rows to skip (header) until measurement data is reached in BUFR file for each profile
    profiles_data = []
    for i, i_prof in enumerate(idx_profs, start=1):
        # if more than one profile in BUFR file, look for the start and end indexed of the profile values
        prof_start_measurement_index = i_prof + skip_rows
        if i == n_prof:   # last or unique profile of file
            prof_end_measurement_index = len(df)
        if i < n_prof:
            prof_end_measurement_index = idx_profs[i] - 1

        prof_start_metadata_index = i_prof
        prof_end_metadata_index = i_prof + skip_rows - 1

        # retrieve profile values
        profile_data = dict()
        for j, (key_id, key_val) in enumerate(BUFR_VAR['data'].items()):
            profile_data[key_id] = df.loc[prof_start_measurement_index:prof_end_measurement_index]["id_value"].loc[
                df["id"] == key_val].astype(float)
        del(j, key_id, key_val)

        # convert temperature to celsius
        if 'temp' in profile_data:
            profile_data['temp'] = round(profile_data['temp'] - KELVIN_TO_CELSIUS, 2)

        # glob_gtspp are qc flags for both depth and temp variable in this order. Need to separate them ...
        profile_data['glob_gtspp_depth'] = profile_data['glob_gtspp'][0::2].values
        profile_data['glob_gtspp_temp'] = profile_data['glob_gtspp'][1::2].values

        # retrieve dimensionless values (lat, lon, time)
        profile_geotime = dict()
        for j, (key_id, key_val) in enumerate(BUFR_VAR['location'].items()):
            profile_geotime[key_id] = df.loc[prof_start_metadata_index:prof_end_metadata_index]["id_value"].loc[
                df["id"] == key_val].astype(float).values[0]
        del(j, key_id, key_val)

        # retrieve date UTC values
        _date = dict()
        for j, (key_id, key_val) in enumerate(BUFR_VAR['date'].items()):
            _date[key_id] = df.loc[prof_start_metadata_index:prof_end_metadata_index]["id_value"].loc[
                df["id"] == key_val].astype(int)
        del(j, key_id, key_val)

        date_utc = datetime.datetime(_date['year'],
                                     _date['month'],
                                     _date['day'],
                                     _date['hour'],
                                     _date['minute'])

        profile_geotime['date_utc'] = date_utc  # store date_utc to profile_geotime

        # retrieve metadata values
        profile_metadata = dict()
        for j, (key_id, key_val) in enumerate(BUFR_VAR['metadata'].items()):
            value = df.loc[prof_start_metadata_index:prof_end_metadata_index]["id_value"].loc[
                df["id"] == key_val].astype(str).values[0].strip("\'").strip("\"")

            if key_val == BUFR_VAR['metadata']['XBT_instrument_serialnumber']:  # serial number value is repeated twice
                # in the BUFR file. The second value is correct
                value = df.loc[prof_start_metadata_index:prof_end_metadata_index]["id_value"].loc[
                    df["id"] == key_val].astype(str).values[1].strip("\'").strip("\"")

            if value not in ('None', None, ''):
                profile_metadata[key_id] = value
        del(j, key_id, key_val)

        profiles_data.append({
            'profile_data': profile_data,
            'profile_geotime': profile_geotime,
            'profile_metadata': profile_metadata
        })

        xbt_recorder_type_val = get_record_type(profiles_data[i-1])

        profiles_data[i-1]['profile_metadata']['XBT_recorder_type'] = \
            'WMO Code table 4770 code \"{code}, {recorder}\"'.format(
                code=profiles_data[i-1]['profile_metadata']['XBT_recorder_type'],
                recorder=xbt_recorder_type_val)

        [probe, code, coef_a, coef_b] = get_fallrate_eq_coef(profiles_data[i-1])
        profile_metadata['XBT_probetype_fallrate_equation'] = \
            'WMO Code Table 1770 \"probe={probe},code={code},a={coef_a},b={coef_a}\"'.format(probe=probe,
                                                                                   code=code,
                                                                                   coef_a=coef_a,
                                                                                   coef_b=coef_b)

    return profiles_data


def xbt_line_get_info(profile, url):
    """
    retrieve xbt line information from ANDS vocabulary and store new values in existing profile dictionary
    :param profile:
    :param url: url of the ANDS xbt line vocabulary
    :return:
    """

    helper = XbtLineVocabHelper(url)
    xbt_lines_info = helper.xbt_line_info()
    xbt_line = profile['profile_metadata']['XBT_line']

    # look for xbt line value from BUFR file available in ANDS XBT line vocabulary
    if xbt_line not in xbt_lines_info:
        raise InvalidFileContentError(
            '{xbt_code} is not a known/correct XBT line value found in the ANDS XBT line vocabulary'.
            format(xbt_code=xbt_line))

    xbt_line_description = xbt_lines_info[xbt_line]['xbt_line_description']
    xbt_line = xbt_lines_info[xbt_line]['xbt_pref_label']

    profile['profile_metadata']['XBT_line'] = xbt_line
    profile['profile_metadata']['XBT_line_description'] = xbt_line_description

    return profile


def fzf_vessel_get_info(profile):
    """
    fuzzy search finder for vessel callsign.
    The vessel name found in the BUFR file format is slightly different from the platform code AODN vocabulary.
    This function finds the closest match and modifies the name of the vessel accordingly with a confidence of 0.9
    :param profile:
    :return: profile
    """
    callsign_list = ship_callsign_list()
    ship_name = profile['profile_metadata']['ship_name']
    ship_name_fuzzy_search = fwprocess.extractOne(ship_name,
                                                  list(callsign_list.values()),
                                                  score_cutoff=90)
    try:
        ship_name = ship_name_fuzzy_search[0]
    except:
        raise InvalidFileContentError('{ship_name} is not a valid enough value to fuzzy match it with an existing AODN'
                                      'vessel name'.format(ship_name=ship_name))

    callsign = next(k for k, v in callsign_list.items() if v == ship_name)  # find callsign from key value
    # special case for the Astrolabe vessel. All NRT XBT data (post 2020) is collected by the new Astrolabe vessel,
    # which has a new callsign.
    # 2 callsigns are available in the ANDS vocabulary for this vessel; We simply force it to use the new vessel only to
    # avoid writing complicated and unnecessary logic
    if callsign == 'FHZI':
        callsign = 'FASB'

    profile['profile_metadata']['ship_name'] = ship_name
    profile['profile_metadata']['Callsign'] = callsign

    return profile


def netcdf_writer(profile_data, output_dir):
    """
    Create a NetCDF from a parsed BUFR csv file
    :param profile_data:
    :param output_dir:
    :return:
    """

    template = ImosTemplate.from_json(NC_JSON_TEMPLATE_BUFR)
    template.global_attributes.update(profile_data['profile_metadata'])

    time_val_dateobj = date2num(profile_data['profile_geotime']['date_utc'],
                                template.variables['TIME']['units'],
                                template.variables['TIME']['calendar'])

    template.variables['TIME']['_data'] = time_val_dateobj
    template.variables['LATITUDE']['_data'] = profile_data['profile_geotime']['latitude']
    template.variables['LONGITUDE']['_data'] = profile_data['profile_geotime']['longitude']

    template.variables['TEMP']['_data'] = profile_data['profile_data']['temp'].values
    template.variables['DEPTH']['_data'] = profile_data['profile_data']['depth'].values

    template.variables['TEMP_quality_control']['_data'] = np.int8(profile_data['profile_data']['glob_gtspp_temp'])
    template.variables['DEPTH_quality_control']['_data'] = np.int8(profile_data['profile_data']['glob_gtspp_depth'])

    _, _, coef_a, coef_b = get_fallrate_eq_coef(profile_data)
    template.variables['DEPTH'].update({'fallrate_equation_coefficient_a': coef_a})
    template.variables['DEPTH'].update({'fallrate_equation_coefficient_b': coef_b})

    # issue with the python-aodntools NetCDF writer package not updating some attributes to the correct type.
    # The following does this manually
    att_to_convert = ["flag_values", "valid_min", "valid_max"]
    for att in att_to_convert:
        for var in ['TEMP_quality_control', 'DEPTH_quality_control']:
            template.variables[var][att] = np.int8(template.variables[var][att])

    template.add_extent_attributes()
    template.add_date_created_attribute()

    abstract = get_info_xbt_config(profile_data['profile_metadata']['XBT_line'])['abstract']
    title = get_info_xbt_config(profile_data['profile_metadata']['XBT_line'])['title']

    template.global_attributes.update({
        'abstract': abstract,
        'title': title,
        'featureType': 'profile',
        'history': "{date_created}: file created".format(
            date_created=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    })

    nc_filename = 'IMOS_SOOP-XBT_T_{date_start}_{xbt_line}_FV00_ID_{imo_number}.nc'.format(
        date_start=datetime.datetime.strftime(profile_data['profile_geotime']['date_utc'], '%Y%m%dT%H%M%SZ'),
        xbt_line=profile_data['profile_metadata']['XBT_line'],
        imo_number=profile_data['profile_metadata']['imo_number']
    )

    netcdf_path = os.path.join(output_dir, nc_filename)
    template.to_netcdf(netcdf_path)
    return netcdf_path


def _config_parser(conf_file):
    """ parse a config file """
    parser = ConfigParser()
    parser.optionxform = str  # to preserve case
    parser.read(conf_file)
    return parser


def get_info_xbt_config(section_name):
    """
    read soop_xbt_config.ini [XBT_LINE_CONFIG] file. Each section "[section]" becomes a dictionary returned by this function.
    The elements of each section is a key of the dictionary
    """
    xbt_config = _config_parser(XBT_CONFIG)
    if section_name in xbt_config.sections():
        return dict(xbt_config.items(section_name))


def get_fallrate_eq_coef(profile):
    """return probe type name, coef_a, coef_b as defined in WMO1770"""
    fre_list = get_info_xbt_config('FRE')
    peq_list = get_info_xbt_config('PEQ$')

    item_val = profile['profile_metadata']['XBT_probetype_fallrate_equation'].zfill(3)  # adding a leading zeros. NRT
    # BUFR files don't have leading zeros in their various metadata code. However DM files do, and the soop_xbt_config.ini was
    # created based on DM files. In order to have a bit of consistency we're adding a leading one '52' becomes '052'

    if len(item_val) > 3:
        # if XBT_probetype_fallrate_equation attribute has already been modified with it's proper string value-> regexp
        item_val = re.match(r'.*code=([0-9]{3}).*', profile['profile_metadata']['XBT_probetype_fallrate_equation']).group(1)

    if item_val in list(fre_list.keys()):
        probetype = peq_list[item_val].split(',')[0]
        coef_a = fre_list[item_val].split(',')[0]
        coef_b = fre_list[item_val].split(',')[1]

        return probetype, item_val, float(coef_a), float(coef_b)
    else:
        raise MissingConfigParameterError('FRE code={code} missing from soop_xbt_config.ini'.format(code=item_val))


def get_record_type(profile):
    """return recorder type in WMO4770"""
    rct_list = get_info_xbt_config('RCT$')

    item_val = profile['profile_metadata']['XBT_recorder_type']
    if item_val in list(rct_list.keys()):
        return rct_list[item_val].split(',')[0]
    else:
        raise MissingConfigParameterError('RCT$ value={value} missing from soop_xbt_config.ini'.format(value=item_val))
