import json
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from aodncore.pipeline import FileType, HandlerBase, PipelineFilePublishType, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodncore.util.misc import get_pattern_subgroups_from_string
from aodntools.ncwriter import DatasetTemplate
from netCDF4 import date2num, Dataset
from pkg_resources import resource_filename

from .ship_callsign import ship_callsign_list

SHIP_CODE = 'VLST'
SOOP_NRT_LOG_PATTERN = re.compile(r"""
                                  EPA_
                                  (?P<facility>SOOP_TMV1)_
                                  (?P<product_code>D2M|M2D|MEL|DEV|M2S|S2M|SYD)_.*
                                  \.log$
                                  """, re.VERBOSE)

NC_JSON_TEMPLATE_MOORING = resource_filename("aodndata", "templates/soop_tmv_nrt_nc_template_mooring.json")
NC_JSON_TEMPLATE_TRAJECTORY = resource_filename("aodndata", "templates/soop_tmv_nrt_nc_template_trajectory.json")

CHLU_PARAMS = {
    'blank': 40,
    'scale': 0.0123
}

TURB_PARAMS = {
    'blank': 50,
    'scale': 0.006
}


def parse_log_file(log_path):
    df = pd.read_csv(log_path, header=None,
                     engine='python',
                     error_bad_lines=False)
    df.columns = ["TIME", "status_flag", "product_code", "distance_from_port_km",
                  "LATITUDE", "LONGITUDE", "TEMP", "PSAL", "CPHL", "TURB"]

    try:
        date_format = '%Y/%m/%d %H:%M:%S'
        df['TIME'] = pd.to_datetime(df['TIME'], format=date_format)
    except ValueError:
        date_format = '%d/%m/%Y %H:%M:%S'
        df['TIME'] = pd.to_datetime(df['TIME'], format=date_format)

    df = df[np.isfinite(df['LATITUDE'])]
    df = df[np.isfinite(df['LONGITUDE'])]

    # force make time monotonic and time not duplicated
    df.set_index('TIME', inplace=True)
    df.sort_index(axis=0, inplace=True)
    df = df[~df.index.duplicated(keep='first')]

    return df


def get_measurement_frequency(df):
    """
    SOOP TMV NRT log files can have some of their records missing latitude and longitude values, which are disregarded
    in the panda df. This results in not necessarely having a time difference of 10 secs or 1 sec between each data
    point. We take then the gradiant, and take the median of this value
    :param df:
    :return: the median time frequency of a panda dataframe
    """
    return df.index.to_series().diff().dt.total_seconds().median()


def transform_count_to_real_val(df):
    """ 1sec files measure FLU2 and TURB in counts. Transforming to CPHL and TURB
    10secs are already in CPHL and TURB
    Ref: https://github.com/aodn/imos-toolbox/blob/spirit/Preprocessing/spiritCountToEngPP.txt
    """

    measurement_frequency = get_measurement_frequency(df)
    if measurement_frequency == 1:
        # transform FLU count data to CPHL
        df['CPHL'] = (df['CPHL'].values - CHLU_PARAMS['blank']) * CHLU_PARAMS['scale']

        # transform TURB count data to TURB
        df['TURB'] = (df['TURB'].values - TURB_PARAMS['blank']) * TURB_PARAMS['scale']
    elif measurement_frequency == 10:
        # Nothing to transform
        pass
    else:
        raise InvalidFileContentError(
            "SOOP NRT input logfile has incorrect delta time. '{measurement_frequency}'. Not belonging to any of "
            "('10 secs', '1 sec').".format(measurement_frequency=measurement_frequency))

    return df


def netcdf_writer(log_path, output_dir, ship_name, meta_path=[]):
    if meta_path != []:
        with open(meta_path, 'r') as f:
            meta_data = json.loads(
                '\n'.join([row for row in f.readlines() if len(row.split('#')) == 1]))  # remove comments
            for ii in range(len(meta_data['calibration'])):
                if meta_data['calibration'][ii]['item'] == 'EFLO':
                    calibration_flo_a0 = float(meta_data['calibration'][ii]['a0'])
                    calibration_flo_a1 = float(meta_data['calibration'][ii]['a1'])
                if meta_data['calibration'][ii]['item'] == 'ESAL':
                    calibration_sal_a0 = float(meta_data['calibration'][ii]['a0'])
                    calibration_sal_a1 = float(meta_data['calibration'][ii]['a1'])
                if meta_data['calibration'][ii]['item'] == 'ETMP':
                    calibration_tmp_a0 = float(meta_data['calibration'][ii]['a0'])
                    calibration_tmp_a1 = float(meta_data['calibration'][ii]['a1'])
                if meta_data['calibration'][ii]['item'] == 'ETURB':
                    calibration_turb_a0 = float(meta_data['calibration'][ii]['a0'])
                    calibration_turb_a1 = float(meta_data['calibration'][ii]['a1'])

    df = parse_log_file(log_path)
    df = transform_count_to_real_val(df)
    log_filename = os.path.basename(log_path)

    fields = get_pattern_subgroups_from_string(log_filename, SOOP_NRT_LOG_PATTERN)
    product_code = fields['product_code']

    if product_code in ['D2M', 'M2D', 'S2M', 'M2S']:
        product_type = "transect"
        feature_type = "trajectory"
        template = DatasetTemplate.from_json(NC_JSON_TEMPLATE_TRAJECTORY)
    elif product_code in ['DEV', 'MEL', 'SYD']:
        product_type = "mooring"
        feature_type = "timeSeries"
        template = DatasetTemplate.from_json(NC_JSON_TEMPLATE_MOORING)
    else:
        raise InvalidFileNameError(
            "SOOP NRT input logfile has incorrect product_code '{product_code}'. Not belonging to any of "
            "('D2M', 'M2D', 'S2M', 'M2S','DEV', 'MEL', 'SYD').".format(product_code=product_code))

    template.global_attributes.update({
        'product_type': product_type})

    time_val_dateobj = date2num(df.index.to_pydatetime(),
                                template.variables['TIME']['units'],
                                template.variables['TIME']['calendar'])

    # replace all nan with FillValue from template value
    df.replace(np.nan, template.variables['LATITUDE']['_FillValue'], inplace=True)

    template.variables['TIME']['_data'] = time_val_dateobj
    template.variables['LATITUDE']['_data'] = df.LATITUDE.values
    template.variables['LONGITUDE']['_data'] = df.LONGITUDE.values

    template.variables['TEMP']['_data'] = df.TEMP.values
    template.variables['PSAL']['_data'] = df.PSAL.values
    template.variables['TURB']['_data'] = df.TURB.values
    template.variables['CPHL']['_data'] = df.CPHL.values

    calibration_comment = 'Value=a0 + a1 x raw_value'
    if 'calibration_tmp_a0' in locals() and 'calibration_tmp_a1' in locals():
        template.variables['TEMP']['a0'] = calibration_tmp_a0
        template.variables['TEMP']['a1'] = calibration_tmp_a1
        template.variables['TEMP']['calibration_comment'] = calibration_comment

    if 'calibration_sal_a0' in locals() and 'calibration_sal_a1' in locals():
        template.variables['PSAL']['a0'] = calibration_sal_a0
        template.variables['PSAL']['a1'] = calibration_sal_a1
        template.variables['PSAL']['calibration_comment'] = calibration_comment

    if 'calibration_turb_a0' in locals() and 'calibration_turb_a1' in locals():
        template.variables['TURB']['a0'] = calibration_turb_a0
        template.variables['TURB']['a1'] = calibration_turb_a1
        template.variables['TURB']['calibration_comment'] = calibration_comment

    if 'calibration_flo_a0' in locals() and 'calibration_flo_a1' in locals():
        template.variables['CPHL']['a0'] = calibration_flo_a0
        template.variables['CPHL']['a1'] = calibration_flo_a1
        template.variables['CPHL']['calibration_comment'] = calibration_comment

    measurement_frequency = get_measurement_frequency(df)
    if measurement_frequency == 1:
        measurement_frequency_str = '1sec'
    elif measurement_frequency == 10:
        measurement_frequency_str = '10secs'

    template.global_attributes.update({
        'time_coverage_start': df.index.strftime('%Y-%m-%dT%H:%M:%SZ')[0],
        'time_coverage_end': df.index.strftime('%Y-%m-%dT%H:%M:%SZ')[-1],
        'featureType': feature_type,
        'date_created': pd.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'platform_code': SHIP_CODE,
        'vessel_name': ship_name,
        'geospatial_lat_min': df.LATITUDE.dropna().min(),
        'geospatial_lat_max': df.LATITUDE.dropna().max(),
        'geospatial_lon_min': df.LONGITUDE.dropna().min(),
        'geospatial_lon_max': df.LONGITUDE.dropna().max(),
        'measurement_frequency': measurement_frequency_str,
        'history': "File created {date_created}".format(
            date_created=pd.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    })

    if measurement_frequency == 1:
        template.variables['CPHL'].update({'calibration_blank': CHLU_PARAMS['blank'],
                                           'calibration_scale': CHLU_PARAMS['scale']
                                           })

        template.variables['TURB'].update({'calibration_blank': TURB_PARAMS['blank'],
                                           'calibration_scale': TURB_PARAMS['scale']
                                           })

    nc_filename = 'IMOS_SOOP-TMV_TSUB_{time_start}_{vessel_code}_FV0{product_number}_{product_type}-{product_code}_END-{time_end}.nc'.format(
        time_start=df.index.strftime('%Y%m%dT%H%M%SZ')[0],
        time_end=df.index.strftime('%Y%m%dT%H%M%SZ')[-1],
        vessel_code=SHIP_CODE,
        product_number=0,
        product_type=product_type,
        product_code=product_code)

    netcdf_path = os.path.join(output_dir, nc_filename)
    template.to_netcdf(netcdf_path)
    return netcdf_path


class SoopTmvNrtHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopTmvNrtHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.log', '.zip']
        self.ship_callsign_ls = None
        self.soop_tmv_dir = None

    def preprocess(self):
        if self.custom_params is not None and self.custom_params.get('ship_callsign_ls'):
            self.ship_callsign_ls = self.custom_params['ship_callsign_ls']
        else:
            self.ship_callsign_ls = ship_callsign_list()

        if SHIP_CODE not in self.ship_callsign_ls:
            raise RuntimeError(
                "Missing vessel callsign {callsign} from vocabulary.".format(callsign=SHIP_CODE))

        self.soop_tmv_dir = os.path.join('IMOS', 'SOOP', 'SOOP-TMV',
                                         '{ship_code}_{ship_name}'.format(ship_code=SHIP_CODE,
                                                                          ship_name=self.ship_callsign_ls[SHIP_CODE]),
                                         'realtime')

        txt_files = self.file_collection.filter_by_attribute_value('extension', '.txt')
        log_files = self.file_collection.filter_by_attribute_value('extension', '.log')
        nc_files = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        """
        * 10secs zip files (*.log + *.txt [calibration]) -> *.zip is pushed to ARCHIVE_DIR
                                                            (netcdf still needs to be generated to deduce path).
                                                            *.log, *.txt and *.nc NOT added to the collection
        * 1sec zip files (*.log only) -> *.log & *.nc pushed to S3. *.zip not added to the collection
        """

        if len(nc_files):
            # case where we re-push an existing NetCDF file
            f_nc = nc_files[0]
            f_nc.publish_type = PipelineFilePublishType.HARVEST_UPLOAD

        elif len(log_files):
            f_log = log_files[0]
            log_filename = os.path.basename(f_log.src_path)

            if SOOP_NRT_LOG_PATTERN.match(log_filename) is None:
                raise InvalidFileNameError(
                    "SOOP TMV NRT input logfile has incorrect naming '{name}'.".format(name=log_filename))

            # case to create NetCDF file from log file
            f_txt = None
            if len(txt_files):
                f_txt = txt_files[0]
                netcdf_filepath = netcdf_writer(f_log.src_path, self.temp_dir, self.ship_callsign_ls[SHIP_CODE],
                                                meta_path=f_txt.src_path)
            else:
                netcdf_filepath = netcdf_writer(f_log.src_path, self.temp_dir, self.ship_callsign_ls[SHIP_CODE])

            # the path of logs and zips has to deduced within the pre-process as it needs the creation of a NetCDF to
            # get the correct info
            with Dataset(netcdf_filepath) as nc_open:
                measurement_frequency = nc_open.measurement_frequency
                product_type = nc_open.product_type
                year = datetime.strptime(nc_open.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")

            pre_path = os.path.join(self.soop_tmv_dir, product_type, measurement_frequency, year)

            if measurement_frequency == "1sec":
                f_log.publish_type = PipelineFilePublishType.UPLOAD_ONLY
                f_log.dest_path = os.path.join(pre_path, 'logs', f_log.name)
                nc_file = PipelineFile(netcdf_filepath)
                nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
                self.file_collection.add(nc_file)

            elif measurement_frequency == "10secs":
                if self.input_file.endswith('zip'):
                    self.input_file_object.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
                    self.input_file_object.archive_path = os.path.join(pre_path, 'logs', self.input_file_object.name)
                    self.file_collection.add(self.input_file_object)
                    f_log.publish_type = PipelineFilePublishType.NO_ACTION
                    if f_txt:
                        f_txt.publish_type = PipelineFilePublishType.NO_ACTION
                else:
                    # case when a 10secs log file (and not a zip) is pushed to incoming
                    f_log.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
                    f_log.archive_path = os.path.join(pre_path, 'logs', f_log.name)

    def dest_path(self, filepath):
        with Dataset(filepath, mode='r') as nc_obj:
            measurement_frequency = nc_obj.measurement_frequency
            product_type = nc_obj.product_type
            year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")

        if measurement_frequency != "1sec":
            raise InvalidFileContentError("SOOP TMV NRT: NetCDF with a measurement frequency of "
                                          "{measurement_frequency} aren't allowed to be harvested".
                                          format(measurement_frequency=measurement_frequency))

        return os.path.join(self.soop_tmv_dir, product_type, measurement_frequency, year, os.path.basename(filepath))
