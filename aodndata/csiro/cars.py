import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError


def dest_path_cars(filepath):
    try:
        pattern = 'CARS(\d+)_.*\.nc'
        year = re.search(pattern, filepath).group(1)
    except AttributeError:
        raise InvalidFileNameError(
            'invalid file name {filepath}. Not matching \'CARS(\d+)_.*\.nc\''.format(filepath=filepath))
    return os.path.join("CSIRO/Climatology/CARS/{year}/AODN-product/{basename}".
                        format(year=year, basename=os.path.basename(filepath)))
