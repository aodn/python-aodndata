import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError, PipelineProcessingError,DuplicatePipelineFileError
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
    "NSW-DPE": 'Department_of_Planning_and_Environment-New_South_Wales',
    "VIC-DEAKIN-UNI": 'Deakin_University',
    "UWA": 'UWA',
    "PPA": "Pilbara_Ports_Authority",
    "GP-VIC": "Gippsland-Ports-Victoria"
}

# - Listing just the institution codes (A|B|C|...|F|G):
INSTITUTION_CODES = '|'.join([i for i in INSTITUTION_PATHNAME.keys()])

# - All files/paths will have Wave-buoy in the file name and dir name:
WAVEBUOY_DIR = 'WAVE-BUOYS'

# - Possible data modes {in filename: in dir name}:
DATA_MODE = {"RT": "REALTIME",
             "DM": "DELAYED"}

DATA_FILE_REGEX = re.compile(r"""
                (?P<institution>BOM|DOT-WA|DTA|DES-QLD|MHL|IMOS_NTP-WAVE|NSW-DPE|VIC-DEAKIN-UNI|UWA|PPA|GP-VIC)_
                (?P<nc_time_cov_start>[0-9]{8}).*_
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
        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
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
                "as part of the collection".format(filename=file_basename, insitution=institution))

        data_base_dir = os.path.join(INSTITUTION_PATHNAME[institution], WAVEBUOY_DIR, mode_dir, data_type)

        site_dir = fields['site_name']
        if mode == 'RT':
            site_dir = fields['site_name']
            year = fields['nc_time_cov_start'][0:4]
            month = fields['nc_time_cov_start'][4:6]
            site_dir = os.path.join(site_dir, year, month)

        return os.path.join(data_base_dir, site_dir, os.path.basename(filepath))

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

        # len
        if len(self.file_collection)>1:
            DuplicatePipelineFileError("ABORTING:More than one file in the file collection")

        input_nc_file = self.file_collection[0]

        if mode == 'RT':
            # check if an aggregated monthly file exist in the destination folder.
            # If a monthly file exist, aggregate the new file
            self.upload_destination = os.path.dirname(AodnWaveHandler.dest_path(self.input_file))
            result = self.state_query.query_storage(self.upload_destination)
            if result:
                if len(result) > 1:
                    raise PipelineProcessingError("More than one file found in monthly folder")

                self.logger.info("Mode '{mode}': found an existing monthly file. Generating updated aggregated "
                                 "product '{remotefile}'."
                             .format(mode=mode, remotefile=result[0].dest_path))
                # No need to add previous file to the Pipelinefilecollection for deletion as it will simply be overwritten.
                # aggregate files and add to pipeline file collection
                self.state_query.download(result, self.temp_dir)
                source_file_path = result[0].local_path
                aggregated_file_path = nrt_timeseries_aggregator.file_aggregator(input_nc_file,
                                                                                 source_file_path,
                                                                                 self.products_dir, fields)
            else:
                #process input_file only to rename it
                self.logger.info("Mode '{mode}': no existing monthly file at : {remotefile}.".
                                 format(mode=mode, remotefile=self.upload_destination))
                aggregated_file_path = nrt_timeseries_aggregator.file_aggregator(input_nc_file, None, self.products_dir,
                                                                                 fields)

            aggregated_file = PipelineFile(aggregated_file_path)
            aggregated_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            input_nc_file.publish_type = PipelineFilePublishType.NO_ACTION
            self.file_collection.add(aggregated_file)

        else:
            if datatype == 'WAVE-PARAMETERS':
                input_nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            elif datatype == 'WAVE-SPECTRA' or 'WAVE-RAW-DISPLACEMENTS':
                input_nc_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            else:
                raise ValueError(
                    "Invalid data type for this collection '{datatype}'".format(datatype=datatype))




