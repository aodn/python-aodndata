import os

from aodncore.pipeline.exceptions import InvalidFileNameError

PREFIX_PATH = 'IMOS/SRS/OC/LJCO/AERONET'
VALID_FILENAME = 'Lucinda.lev20'


def dest_path_srs_oc_ljco_aeronet(filepath):
    file_basename = os.path.basename(filepath)

    if file_basename == VALID_FILENAME:
        return os.path.join(PREFIX_PATH, file_basename)

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not equal to {valid} in order to deduce dest_path".format(
                filename=os.path.basename(filepath),
                valid=VALID_FILENAME))
