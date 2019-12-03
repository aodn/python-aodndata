import os
from aodncore.pipeline.exceptions import InvalidFileNameError

from netCDF4 import Dataset

__all__ = [
    'dest_path_aatams_sattag_qc_ctd'
]

AATAMS_MEOP_DIR = os.path.join('IMOS', 'AATAMS', 'satellite_tagging', 'MEOP_QC_CTD')


def dest_path_aatams_sattag_qc_ctd(filepath):

    with Dataset(filepath, mode='r') as nc_obj:
        try:
            deployment_code = nc_obj.deployment_code
        except AttributeError:
            raise InvalidFileNameError('deployment_code attribute not found in NetCDF file to deduce path')

    # deployment code should be equivalent to the start of the NetCDF
    netcdf_filename = os.path.basename(filepath)
    if deployment_code != netcdf_filename[0:len(deployment_code)]:
        raise InvalidFileNameError('Empty deployment_code attribute in NetCDF file to deduce path')

    return os.path.join(AATAMS_MEOP_DIR, deployment_code, netcdf_filename)
