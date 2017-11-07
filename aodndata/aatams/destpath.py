import os

from netCDF4 import Dataset

__all__ = [
    'dest_path_aatams_sattag_qc_ctd'
]


def dest_path_aatams_sattag_qc_ctd(filepath):
    aatams_meop_dir = os.path.join('AATAMS', 'satellite_tagging', 'MEOP_QC_CTD')
    netcdf_file_obj = Dataset(filepath, mode='r')
    deployment_code = netcdf_file_obj.deployment_code
    netcdf_file_obj.close()

    netcdf_filename = os.path.basename(filepath)
    relative_netcdf_path = os.path.join(aatams_meop_dir, deployment_code,
                                        netcdf_filename)

    return relative_netcdf_path
