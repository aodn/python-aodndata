import os
from datetime import datetime

from aodncore.pipeline import HandlerBase, FileType, PipelineFilePublishType
from netCDF4 import Dataset

"""
Processing MMP CTD data from AIMS
"""
def dest_path_aims_mmp_ctd(filepath):
    nc_obj = Dataset(filepath, mode='r')
    year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")

    return os.path.join('AIMS', 'Marine_Monitoring_Program', 'CTD_profiles',
                            year, os.path.basename(filepath))
