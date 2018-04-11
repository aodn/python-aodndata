import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError


def dest_path_sstaars(filepath):
    sstaars_alt_dir = os.path.join('CSIRO', 'Climatology', 'SSTAARS', '2017')
    sstaars_aodn_dir = os.path.join(sstaars_alt_dir, 'AODN-product')
    netcdf_file_name = os.path.basename(filepath)

    regex_daily_files = re.compile('SSTAARS_daily_fit_[0-9]{3}\.nc')

    if netcdf_file_name == 'SSTAARS.nc':
        return os.path.join(sstaars_alt_dir, netcdf_file_name)
    elif (netcdf_file_name == 'SSTAARS_daily_fit.nc') or re.match(regex_daily_files, netcdf_file_name):
        return os.path.join(sstaars_aodn_dir, netcdf_file_name)
    else:
        raise InvalidFileNameError(
            'invalid file name {filepath}. Not matching \'CARS(\d+)_.*\.nc\''.format(filepath=filepath))
