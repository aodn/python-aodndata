import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.pipeline import HandlerBase, PipelineFilePublishType
from aodncore.util.misc import get_pattern_subgroups_from_string

# Defining global variables:
# - Defining all the possible Institutions that provides us with data (the acronym and the dir name for each):
INSTITUTION_PATHNAME = {
    "BOM": 'Bureau_of_Meteorology',
    "DOT-WA": 'Department_of_Transport-Western_Australia',
    "DTA": 'Defence_Technology_Agency-New_Zealand',
    "DES-QLD": 'Department_of_Environment_and_Science-Queensland',
    "MHL": 'Manly_Hydraulics_Laboratory',
    "IMOS_NTP-WAVE": 'IMOS/NTP/Low_Cost_Wave_Buoy_Technology',
    "NSW-DPE": 'Department_of_Planning_and_Environment-New_South_Wales',
    "VIC-DEAKIN-UNI": 'Deakin_University',
    "UWA": 'UWA'
}

# - Listing just the institution codes (A|B|C|...|F|G):
INSTITUTION_CODES = '|'.join([i for i in INSTITUTION_PATHNAME.keys()])

# - All files/paths will have Wave-buoy in the file name and dir name:
WAVEBUOY_DIR = 'WAVE-BUOYS'

# - Possible data modes {in filename: in dir name}:
DATA_MODE = {"RT": "REALTIME",
             "DM": "DELAYED"}

DATA_FILE_REGEX = re.compile(r"""
                (?P<institution>BOM|DOT-WA|DTA|DES-QLD|MHL|IMOS_NTP-WAVE|NSW-DPE|VIC-DEAKIN-UNI|UWA)_
                (?P<nc_time_cov_start>[0-9]{8})_
                (?P<site_name>(.*))_
                (?P<mode>RT|DM)_
                (?P<datatype>WAVE-PARAMETERS|WAVE-SPECTRA|WAVE-RAW-DISPLACEMENTS)_END-
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

        mode = re.search('RT|DM', file_basename)
        if mode is None:
            raise InvalidFileNameError(
                "file name: \"{filename}\" has data mode (RT or DM) missing or incorrect".format(
                    filename=file_basename))
        else:
            data_mode = mode.group(0)

        mode_dir = DATA_MODE[data_mode]

        type = re.search('WAVE-PARAMETERS|WAVE-SPECTRA|WAVE-RAW-DISPLACEMENTS', file_basename)
        if type is None:
            raise InvalidFileNameError(
                "file name: \"{filename}\" has incorrect data type that is not part of the collection".format(
                    filename=file_basename))
        else:
            data_type = type.group(0)

        inst = re.search(INSTITUTION_CODES, file_basename)
        if inst is None:
            raise InvalidFileNameError(
                "file name: \"{filename}\" has incorrect institution which is not listed as part of the collection"
                .format(filename=file_basename))
        else:
            institution = inst.group(0)

        data_base_dir = os.path.join(INSTITUTION_PATHNAME[institution], WAVEBUOY_DIR, mode_dir, data_type)
        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
        product_dir = fields['site_name']
        if data_mode == 'RT':
            year = fields['nc_time_cov_start'][0:4]
            month = fields['nc_time_cov_start'][4:6]
            product_dir = os.path.join(product_dir, year, month)

        return os.path.join(data_base_dir, product_dir, os.path.basename(filepath))

    def preprocess(self):
        """
        Set integral wave parameters delayed mode and realtime files destination path based on file attributes
         files have to be uploaded to S3 and are not harvested
        """
        file_basename = os.path.basename(self.input_file)
        fields = get_pattern_subgroups_from_string(file_basename, DATA_FILE_REGEX)
        datatype = fields['datatype']

        nc = self.file_collection[0]
        if datatype == 'WAVE-PARAMETERS':
            nc.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
        elif datatype == 'WAVE-SPECTRA' or 'WAVE-RAW-DISPLACEMENTS':
            nc.publish_type = PipelineFilePublishType.UPLOAD_ONLY
        else:
            raise ValueError(
                "Invalid data type for this collection '{datatype}'".format(datatype=datatype))
