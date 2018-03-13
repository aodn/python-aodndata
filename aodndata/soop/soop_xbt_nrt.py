import os

from aodncore.pipeline.exceptions import InvalidFileNameError

def dest_path_soop_xbt_nrt(filepath):
    " return the path of a CSV SOOP XBT NRT file stored in $WIP_DIR containing the string sbddata"
    try:
        rel_path = filepath.split("sbddata/", 1)[1]
    except IndexError:
        raise InvalidFileNameError(
            'invalid file name {filepath}. Subdirectory \'sbddata\' not found in path, unable to split'.format(filepath=filepath))
    return os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME', rel_path)
