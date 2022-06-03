import os
import re

from netCDF4 import Dataset
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileNameError, InvalidFileFormatError, \
    InvalidInputFileError
from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.util.misc import get_pattern_subgroups_from_string

# Defining global variables:
# - Defining all the possible Institutions that provides us with data (the acronym and the dir name for each):
INSTITUTION_PATHNAME = {
    "BOM": 'Bureau_of_Meteorology',
    "DOT-WA": 'Department_of_Transport-Western_Australia',
    "DTA": 'Defence_Technology_Agency-New_Zealand',
    "DES-QLD": 'Department_of_Environment_and_Science-Queensland',
    "IMOS_ANMN-NSW": '?',
    "MHL": 'Manly_Hydraulics_Laboratory',
    "IMOS_NTP-WAVE": 'IMOS/NTP/Low_Cost_Wave_Buoy_Technology',
    "NSW-DPE": 'Department_of_Planning_and_Environment-New_South_Wales',
    "VIC-DEAKIN-UNI": 'Deakin_University',
    "UWA": 'UWA'
}

# - Listing just the institution codes (A|B|C|...|F|G):
INSTITUTION_CODES = '|'.join([i for i in INSTITUTION_PATHNAME.keys()])

# - All files/paths will have Wave-buoy in the file name and dir name:
WAVEBUOY_DIR = 'Wave_Buoys'

# - Possible data modes {in filename: in dir name}:
DATA_MODE = {"RT": "Realtime",
             "DM": "Delayed"}

# - Possible data types {in filename: in dir name}:
DATA_TYPES = {"WAVE-PARAMETERS": 'Wave-parameters',
              "SPECTRA": 'Spectra',
              "RAW-DISPLACEMENTS": 'Raw-displacements'}

# - Listing just the data types (A|B|C|...|F|G):
DATA_TYPES_REGEX = '|'.join([t for t in DATA_TYPES.keys()])

DATA_FILE_REGEX = re.compile(r"""
                (?P<institution>BOM|DOT-WA|DTA|DES-QLD|IMOS_ANMN-NSW|MHL|IMOS_NTP-WAVE|NSW-DPE|VIC-DEAKIN-UNI|UWA)_
                (?P<nc_time_cov_start>[0-9]{8})_
                (?P<site_name>(.*))_
                (?P<mode>RT|DM)_
                (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                (?P<nc_time_cov_end>[0-9]{8})\.nc$
                """, re.VERBOSE)


class AodnWaveHandler(HandlerBase):
    """Handling AODN wave data files in Near Realtime or Delayed mode. It handles the following types of NetCDF files:
     * Integral wave parameters data files in Delayed mode and Near Realtime, which are harvested;
     * Spectral data files only in Delayed mode, which are just uploaded to S3;
     * Raw displacement data files only in Delayed mode, which are just uploaded to S3.
    """

    def __init__(self, *args, **kwargs):
        super(AodnWaveHandler, self).__init__(*args, **kwargs)

    @staticmethod
    def dest_path(filepath):
        file_basename = os.path.basename(filepath)

        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)

        mode = fields['mode']
        mode_dir = DATA_MODE[mode]

        datatype = fields['datatype']
        datatype_dir = DATA_TYPES[datatype]

        institution = fields['institution']

        data_base_dir = os.path.join(INSTITUTION_PATHNAME[institution], WAVEBUOY_DIR, mode_dir, datatype_dir)
        product_dir = fields['site_name']

        return os.path.join(data_base_dir, product_dir, os.path.basename(filepath))

    def preprocess(self):
        """
        Set integral wave parameters delayed mode and realtime files destination path based on file attributes
         files have to be uploaded to S3 and are not harvested
        """
        file_basename = os.path.basename(self.input_file)
        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
        datatype = fields['datatype']
        if datatype == 'WAVE-PARAMETERS':
            self.input_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            print("harvested")
        elif datatype == 'SPECTRA' or 'RAW-DISPLACEMENTS':
            self.input_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            print("S3")
        else:
            raise ValueError(
                "Invalid data type for this collection '{datatype}'".format(datatype=datatype))

