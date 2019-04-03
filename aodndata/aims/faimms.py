import os
import re
from datetime import datetime

from aodncore.pipeline.exceptions import InvalidFileFormatError
from aodncore.pipeline.handlerbase import HandlerBase
from netCDF4 import Dataset


class FaimmsHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(FaimmsHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.dir_manifest']

    @staticmethod
    def get_main_faimms_var(filepath):
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
        main_var = self.get_main_faimms_var(filepath)
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
    def get_faimms_site_name(filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        site_code = netcdf_file_obj.site_code
        netcdf_file_obj.close()

        site_codes = {'DAV': 'Davies_Reef',
                      'OI': 'Orpheus_Island',
                      'OTI': 'One_Tree_Island',
                      'RIB': 'Rib_Reef',
                      'MRY': 'Myrmidon_Reef',
                      'LIZ': 'Lizard_Island',
                      'HI': 'Heron_Island'}

        main_site_code = [site for site in site_codes.keys() if site in site_code]

        if len(main_site_code) != 0:
            return site_codes[main_site_code[0]]
        else:
            raise InvalidFileFormatError(
                "Don't know where to put file '{name}' (Unknown site name)".format(name=os.path.basename(filepath))
            )

    @staticmethod
    def get_faimms_platform_type(filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        site_code = netcdf_file_obj.site_code
        netcdf_file_obj.close()

        if 'SF' in site_code:
            site_code_number = re.findall(r'\d+', site_code)
            return 'Sensor_Float_%s' % str(site_code_number[0])
        elif 'RP' in site_code:
            site_code_number = re.findall(r'\d+', site_code)
            return 'Relay_Pole_%s' % str(site_code_number[0])
        elif 'BSE' in site_code or 'WS' in site_code:
            return 'Weather_Station_Platform'
        else:
            raise InvalidFileFormatError(
                "Don't know where to put file '{name}' (Unknown platform type)".format(name=os.path.basename(filepath))
            )

    def get_main_faimms_site_name_path(self, filepath):
        site_name = self.get_faimms_site_name(filepath)
        platform_type = self.get_faimms_platform_type(filepath)

        return os.path.join(site_name, platform_type)

    @staticmethod
    def remove_md5_from_filename(filepath):
        return re.sub('.[0-9a-z]*.nc$', '.nc', filepath)

    def dest_path(self, filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        file_version = netcdf_file_obj.file_version
        main_var_folder = self.get_main_var_folder_name(filepath)

        if file_version == "Level 0 - Raw data":
            level_name = 'NO_QAQC'
        elif file_version == 'Level 1 - Quality Controlled Data':
            level_name = 'QAQC'

        year = datetime.strptime(netcdf_file_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")
        netcdf_file_obj.close()

        site_name_path = self.get_main_faimms_site_name_path(filepath)
        filepath = self.remove_md5_from_filename(os.path.basename(filepath))
        relative_netcdf_path = os.path.join('IMOS', 'FAIMMS', site_name_path, main_var_folder, year, level_name,
                                            filepath)

        return relative_netcdf_path
