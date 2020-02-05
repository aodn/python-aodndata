import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError


def dest_path_cars(filepath):
    pattern = r'CARS(\d+)_.*\.nc'
    try:
        year = re.search(pattern, filepath).group(1)
    except AttributeError:
        raise InvalidFileNameError(
            "invalid file name {filepath}. Not matching '{pattern}'".format(filepath=filepath, pattern=pattern))
    return os.path.join("CSIRO/Climatology/CARS/{year}/AODN-product/{basename}".
                        format(year=year, basename=os.path.basename(filepath)))
