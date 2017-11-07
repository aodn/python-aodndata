import os
import re

from netCDF4 import Dataset

from aodncore.pipeline.handlerbase import HandlerBase


class AnmnNrsAimsHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(AnmnNrsAimsHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def get_main_anmn_nrs_var(filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        variables = netcdf_file_obj.variables.keys()
        netcdf_file_obj.close()

        del variables[variables.index('TIME')]
        del variables[variables.index('LATITUDE')]
        del variables[variables.index('LONGITUDE')]

        if 'NOMINAL_DEPTH' in variables:
            del variables[variables.index('NOMINAL_DEPTH')]

        qc_var = [s for s in variables if '_quality_control' in s]
        if qc_var != []:
            del variables[variables.index(qc_var[0])]

        return variables[0]

    def get_main_var_folder_name(self, filepath):
        main_var = self.get_main_anmn_nrs_var(filepath)
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

    @staticmethod
    def get_anmn_nrs_site_name(filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        site_code = netcdf_file_obj.site_code
        netcdf_file_obj.close()

        return site_code

    @staticmethod
    def remove_md5_from_filename(filepath):
        return re.sub('.[0-9a-z]*.nc$', '.nc', filepath)

    @staticmethod
    def add_site_code_to_filename(filepath, site_code):
        return re.sub('(?=[^0-9]{6})Z_.*_FV0', 'Z_%s_FV0' % site_code, filepath)

    def dest_path(self, filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        file_version = netcdf_file_obj.file_version
        main_var_folder = self.get_main_var_folder_name(filepath)

        if file_version == "Level 0 - Raw data":
            level_name = 'NO_QAQC'
        elif file_version == 'Level 1 - Quality Controlled Data':
            level_name = 'QAQC'

        year = netcdf_file_obj.time_coverage_start[0:4]
        netcdf_file_obj.close()

        site_code = self.get_anmn_nrs_site_name(filepath)
        filepath = self.remove_md5_from_filename(os.path.basename(filepath))
        filepath = self.add_site_code_to_filename(filepath, site_code)
        relative_netcdf_path = os.path.join('IMOS', 'ANMN', 'NRS', 'REAL_TIME', site_code, main_var_folder, year, level_name,
                                            filepath)

        return relative_netcdf_path
