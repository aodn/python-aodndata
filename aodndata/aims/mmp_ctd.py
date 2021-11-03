import os
from datetime import datetime

from netCDF4 import Dataset

"""
Processing MMP CTD data from AIMS
"""


def dest_path_mmp_ctd(filepath):
    nc_obj = Dataset(filepath, mode='r')
    year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")
    site_short_name = nc_obj.site_short_name

    return os.path.join('AIMS', 'Marine_Monitoring_Program', site_short_name, 'Biogeochem_profiles', year, '{filename}'.
                        format(filename=os.path.basename(filepath)))
