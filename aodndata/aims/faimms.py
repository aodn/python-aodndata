import os
import re

from aodncore.pipeline.exceptions import InvalidFileFormatError
from aodncore.pipeline.handlerbase import HandlerBase
from netCDF4 import Dataset

from aodndata.aims.common import get_main_var_folder_name, get_product_version, get_site_code, get_year, \
    remove_md5_from_filename


class FaimmsHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(FaimmsHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.dir_manifest']

    @staticmethod
    def get_faimms_site_name(filepath):
        site_codes = {'DAV': 'Davies_Reef',
                      'OI': 'Orpheus_Island',
                      'OTI': 'One_Tree_Island',
                      'RIB': 'Rib_Reef',
                      'MRY': 'Myrmidon_Reef',
                      'LIZ': 'Lizard_Island',
                      'HI': 'Heron_Island'}

        site_code = get_site_code(filepath)
        main_site_code = [site for site in site_codes.keys() if site in site_code]

        if len(main_site_code) != 0:
            return site_codes[main_site_code[0]]
        else:
            raise InvalidFileFormatError(
                "Don't know where to put file '{name}' (Unknown site name)".format(name=os.path.basename(filepath))
            )

    @staticmethod
    def get_faimms_platform_type(filepath):
        with Dataset(filepath, mode='r') as netcdf_file_obj:
            site_code = netcdf_file_obj.site_code

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

    def dest_path(self, filepath):
        year = get_year(filepath)
        main_var_folder = get_main_var_folder_name(filepath)
        level_name = get_product_version(filepath)

        site_name_path = self.get_main_faimms_site_name_path(filepath)
        filepath = remove_md5_from_filename(os.path.basename(filepath))

        relative_netcdf_path = os.path.join('IMOS', 'FAIMMS', site_name_path, main_var_folder, year, level_name,
                                            filepath)

        return relative_netcdf_path
