import os
from datetime import datetime

from netCDF4 import Dataset

"""
Processing of soop radiometer data via DALEC and contributed by Pete Fearns
"""


def dest_path_soop_rad_aodn(filepath):
    nc_obj = Dataset(filepath, mode='r')
    year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")

    return os.path.join('Curtin_University', 'Radiometer_DALEC', 'Unknown_Vessels', year, '{filename}'.
                        format(filename=os.path.basename(filepath)))
