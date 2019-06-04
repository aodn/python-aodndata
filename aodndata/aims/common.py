import re
from datetime import datetime

from netCDF4 import Dataset


def get_main_var(filepath):
    with Dataset(filepath, mode='r') as netcdf_file_obj:
        variables = netcdf_file_obj.variables.keys()

    variables.remove('TIME')
    variables.remove('LATITUDE')
    variables.remove('LONGITUDE')

    if 'NOMINAL_DEPTH' in variables:
        variables.remove('NOMINAL_DEPTH')

    qc_var = [s for s in variables if '_quality_control' in s]
    if qc_var != []:
        variables.remove(qc_var[0])  # there is only ONE main variable per NetCDF

    return variables[0]


def get_main_var_folder_name(filepath):
    main_var = get_main_var(filepath)
    netcdf_file_obj = Dataset(filepath, mode='r')
    var_folder_name = netcdf_file_obj.variables[main_var].long_name.replace(' ', '_')
    aims_channel_id = netcdf_file_obj.aims_channel_id

    if hasattr(netcdf_file_obj.variables[main_var], 'sensor_depth'):
        sensor_depth = netcdf_file_obj.variables[main_var].sensor_depth
        retval = '%s@%sm_channel_%s' % (var_folder_name, str(sensor_depth), str(aims_channel_id))
    else:
        retval = '%s_channel_%s' % (var_folder_name, str(aims_channel_id))

    netcdf_file_obj.close()
    return retval


def remove_md5_from_filename(filepath):
    return re.sub('\.[0-9a-z]{32}\.nc$', '.nc', filepath)


def get_product_version(filepath):
    with Dataset(filepath, mode='r') as netcdf_file_obj:
        file_version = netcdf_file_obj.file_version

    file_version_dict = {"Level 0 - Raw data": 'NO_QAQC',
                         'Level 1 - Quality Controlled Data': 'QAQC'}

    return file_version_dict.get(file_version)


def get_year(filepath):
    with Dataset(filepath, mode='r') as netcdf_file_obj:
        return datetime.strptime(netcdf_file_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")


def get_site_code(filepath):
    with Dataset(filepath, mode='r') as netcdf_file_obj:
        return netcdf_file_obj.site_code
