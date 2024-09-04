import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError, DuplicatePipelineFileError
from aodncore.pipeline import PipelineFile, HandlerBase, PipelineFilePublishType
from aodncore.util.misc import get_pattern_subgroups_from_string

from . import nrt_timeseries_aggregator

# Defining global variables:
# - Defining all the possible Institutions that provides us with data (the acronym and the dir name for each):
INSTITUTION_PATHNAME = {
    "BOM": 'Bureau_of_Meteorology',
    "DOT-WA": 'Department_of_Transport-Western_Australia',
    "DTA": 'Defence_Technology_Agency-New_Zealand',
    "DES-QLD": 'Department_of_Environment_and_Science-Queensland',
    "MHL": 'Department_of_Planning_and_Environment-New_South_Wales/Manly_Hydraulics_Laboratory',
    "IMOS_NTP-WAVE": 'IMOS/NTP/Low_Cost_Wave_Buoy_Technology',
    "IMOS_ANMN-DEEP-WATER-WAVES": 'IMOS/ANMN/Deep_Water_Waves',
    "IMOS_ANMN-WAVE-BUOYS": 'IMOS/ANMN/Wave_Buoys',
    "NSW-DPE": 'Department_of_Planning_and_Environment-New_South_Wales',
    "NSW": 'Department_of_Planning_and_Environment-New_South_Wales',
    "VIC-DEAKIN-UNI": 'Deakin_University',
    "UWA": 'UWA',
    "PPA": "Pilbara_Ports_Authority",
    "GP-VIC": "Gippsland-Ports-Victoria",
    "SA-FLINDERS": "Flinders_University"
}

# - Listing just the institution codes (A|B|C|...|F|G):
INSTITUTION_CODES = '|'.join([i for i in INSTITUTION_PATHNAME.keys()])

# - All files/paths will have Wave-buoy in the file name and dir name:
WAVEBUOY_DIR = 'WAVE-BUOYS'

# - Possible data modes {in filename: in dir name}:
DATA_MODE = {"RT": "REALTIME",
             "DM": "DELAYED"}

DATA_FILE_REGEX = re.compile(r"""
                (?P<institution>BOM|DOT-WA|DTA|DES-QLD|MHL|IMOS_NTP-WAVE|IMOS_ANMN-DEEP-WATER-WAVES|
                IMOS_ANMN-WAVE-BUOYS|NSW|NSW-DPE|VIC-DEAKIN-UNI|UWA|PPA|GP-VIC|SA-FLINDERS)_
                (?P<nc_time_cov_start>[0-9]{8}|[0-9]{8}T[0-9]{6}Z)_
                (?P<site_name>(.*))_
                (?P<mode>RT|DM)_
                (?P<datatype>WAVE-PARAMETERS|WAVE-SPECTRA|WAVE-RAW-DISPLACEMENTS)_.*
                \.nc$
                """, re.VERBOSE)


class AodnWaveHandler(HandlerBase):
    """Handling AODN wave data files in Near Realtime or Delayed mode. It handles the following types of NetCDF files:
     * Integral wave parameters data files in Delayed mode and Near Realtime, which are harvested;
     * Spectral data files only in Delayed mode, which are just uploaded to S3;
     * Raw displacement data files only in Delayed mode, which are just uploaded to S3.
    """

    def __init__(self, *args, **kwargs):
        super(AodnWaveHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']
        # store the NC file and the subsequent upload destination calculated from it in the class for other file types
        # to access it when they need to (e.g. dest_path)
        self.upload_destination = None

    @staticmethod
    def dest_path(filepath):
        file_basename = os.path.basename(filepath)
        number_of_fields = file_basename.split('_')
        if number_of_fields[0] == 'IMOS':
            if len(number_of_fields) > 7:
                raise InvalidFileNameError(
                    "file name: '{filename}' invalid. Please check site name: should be - not _ separated".format(
                        filename=file_basename))
        else:
            if len(number_of_fields) > 6:
                raise InvalidFileNameError(
                    "file name: '{filename}' invalid. Please check site name: should be - not _ separated".format(
                        filename=file_basename))

        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
        if len(fields) == 0:
            raise InvalidFileNameError(
                "file name: '{filename}' has invalid filename".format(
                    filename=file_basename))
        mode = fields['mode']
        if mode is None:
            raise InvalidFileNameError(
                "file name: '{filename}' has data mode (RT or DM) missing or incorrect".format(
                    filename=file_basename))

        mode_dir = DATA_MODE[mode]

        data_type = fields['datatype']
        if data_type is None:
            raise InvalidFileNameError(
                "file name: '{filename}' has incorrect data type '{type}'that is not part of the collection".format(
                    filename=file_basename, type=data_type))

        institution = fields['institution']
        if institution is None:
            raise InvalidFileNameError(
                "file name: '{filename}' has incorrect institution '{institution}' which is not listed "
                "as part of the collection".format(filename=file_basename, institution=institution))

        data_base_dir = os.path.join(INSTITUTION_PATHNAME[institution], WAVEBUOY_DIR, mode_dir, data_type)

        site_dir = fields['site_name']
        if mode == 'RT':
            site_dir = os.path.join(fields['site_name'], fields['nc_time_cov_start'][0:4])
            filebasename = nrt_timeseries_aggregator.make_monthly_product_name(fields)
        else:
            filebasename = file_basename
        return os.path.join(data_base_dir, site_dir, filebasename)

    @staticmethod
    def archive_path(filepath):
        file_basename = os.path.basename(filepath)
        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
        data_base_dir = os.path.join(INSTITUTION_PATHNAME[fields['institution']],
                                     WAVEBUOY_DIR, DATA_MODE[fields['mode']], fields['datatype'])
        site_dir = os.path.join(fields['site_name'], fields['nc_time_cov_start'][0:4])

        return os.path.join(data_base_dir, site_dir,file_basename)

    def preprocess(self):
        """
        Set integral wave parameters delayed mode and realtime files destination path based on file attributes
        files have to be uploaded to S3 and are not harvested
        """
        file_basename = os.path.basename(self.input_file)
        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
        if not fields:
            raise InvalidFileNameError("Incorrect file name: '{file}'".format(file=file_basename))

        datatype = fields['datatype']
        mode = fields['mode']
        institution = fields['institution']

        if len(self.file_collection) > 1:
            DuplicatePipelineFileError("ABORTING:More than one file in the file collection")

        input_nc_file = self.file_collection[0]
        # Specific processing of BOM-sourced files because of aggregation of hourly file into monthly product -
        # Excludes monthly files(when repushed) from aggregation

        if mode == 'RT' and re.match('BOM|DOT-WA|DES-QLD|MHL|GP-VIC|IMOS_ANMN-DEEP-WATER-WAVES|IMOS_ANMN-WAVE-BUOYS',
                                     institution) and not re.search('monthly.nc', file_basename):
            # deduce target monthly file name
            target_month = institution + '_' + fields['nc_time_cov_start'][0:6]

            monthly_file_regex = target_month + r"\d{2}_.*" + mode + '_' + datatype + '_monthly.nc'
            # check if an aggregated monthly file exist in the destination folder.
            # If a monthly file exists, aggregate the new file
            self.upload_destination = os.path.dirname(AodnWaveHandler.dest_path(self.input_file))
            result = self.state_query.query_storage(os.path.join(self.upload_destination,target_month))

            existing_monthly_file = result.filter_by_attribute_regex('name', monthly_file_regex)
            if existing_monthly_file:
                self.logger.info("Mode '{mode}': found an existing monthly file. Generating updated aggregated "
                                 "product '{remotefile}'."
                                 .format(mode=mode, remotefile=existing_monthly_file[0].dest_path))
                # No need to add previous file to the Pipelinefilecollection for deletion as it will simply
                # be overwritten. Aggregate files and add to pipeline file collection
                self.state_query.download(existing_monthly_file, self.temp_dir)
                source_file_path = existing_monthly_file[0].local_path
                aggregated_file_path = nrt_timeseries_aggregator.file_aggregator(input_nc_file,
                                                                                 source_file_path,
                                                                                 self.products_dir, fields)
                aggregated_file = PipelineFile(aggregated_file_path)
                self.file_collection.add(aggregated_file)
                aggregated_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
                input_nc_file.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
            else:
                # input_file will be renamed (through dest_path)
                self.logger.info("Mode '{mode}': no existing monthly file at : {remotefile}.".
                                 format(mode=mode, remotefile=self.upload_destination))
                input_nc_file.publish_type = PipelineFilePublishType.HARVEST_ARCHIVE_UPLOAD

        else:
            if datatype == 'WAVE-PARAMETERS':
                input_nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            elif datatype == 'WAVE-SPECTRA' or 'WAVE-RAW-DISPLACEMENTS':
                input_nc_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            else:
                raise ValueError(
                    "Invalid data type for this collection '{datatype}'".format(datatype=datatype))
