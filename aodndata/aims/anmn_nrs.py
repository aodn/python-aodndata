import os
import re

from aodncore.pipeline.handlerbase import HandlerBase

from aodndata.aims.common import get_main_var_folder_name, get_year, get_product_version, get_site_code, \
    remove_md5_from_filename


class AnmnNrsAimsHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(AnmnNrsAimsHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.dir_manifest']


    @staticmethod
    def add_site_code_to_filename(filepath, site_code):
        return re.sub('(?=[^0-9]{6})Z_.*_FV0', 'Z_%s_FV0' % site_code, filepath)

    def dest_path(self, filepath):
        year = get_year(filepath)
        main_var_folder = get_main_var_folder_name(filepath)
        level_name = get_product_version(filepath)

        site_code = get_site_code(filepath)
        filepath = remove_md5_from_filename(os.path.basename(filepath))

        filepath = self.add_site_code_to_filename(filepath, site_code)
        relative_netcdf_path = os.path.join('IMOS', 'ANMN', 'NRS', 'REAL_TIME',
                                            site_code, main_var_folder, year, level_name,
                                            filepath)

        return relative_netcdf_path
