import os
import re
from datetime import datetime

from aodncore.pipeline import HandlerBase
from aodncore.pipeline.exceptions import InvalidFileNameError


class SrsOcGriddedHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsOcGriddedHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def dest_path(filepath):
        gridded_oc_prefix_path = 'IMOS/SRS/OC/gridded'
        srs_oc_gridded_variables_ls = ['chl_gsm', 'chl_oc3', 'chl_oc4', 'dt', 'ipar', 'K_490', 'l2_flags',
                                     'nanop_brewin2010at', 'nanop_brewin2012in', 'npp_vgpm_eppley_gsm',
                                     'npp_vgpm_eppley_oc3', 'npp_vgpm_eppley_oc4', 'owtd', 'par', 'picop_brewin2010at',
                                     'picop_brewin2012in', 'sst', 'sst_quality', 'tsm_clark16', 'tsm_clark']
        oc_variables = '|'.join(srs_oc_gridded_variables_ls)

        if 'P1D' in filepath or 'P1H' in filepath :
            m = re.search(r'^(A|S)\.(P1D|P1H)\.([0-9]{8}T[0-9]{6}Z)\.(aust|overpass)\.(%s)\.nc$' % oc_variables, filepath)
            if m is None:
                raise InvalidFileNameError("file name: \"{filename}\" not matching regex to deduce dest_path for srs oc gridded seawifs/aqua".format(filename=os.path.basename(filepath)))
            else:
                nc_time_cov_start = datetime.strptime(m.group(3), '%Y%m%dT%H%M%SZ')

                if m.group(1) == 'A':
                    product_name = 'aqua'
                elif m.group(1) == 'S':
                    product_name = 'seawifs'

                path = os.path.join(gridded_oc_prefix_path, product_name, m.group(2),
                                    '%d' % nc_time_cov_start.year, '%02d' % nc_time_cov_start.month,
                                    os.path.basename(filepath))
                return path

        elif 'Johnson' in filepath:
            m = re.search(r'^(A|S)([0-9]{14})\.L3m_(8D|MO)_SO_Chl_9km\.Johnson_SO_Chl\.nc$', filepath)

            if m is None:
                raise InvalidFileNameError(
                    "file name: \"{filename}\" not matching regex to deduce dest_path for srs oc gridded contributed data set".format(filename=os.path.basename(filepath)))
            else:

                if m.group(1) == 'A':
                    product_name = 'aqua'
                elif m.group(1) == 'S':
                    product_name = 'seawifs'

                if m.group(3) == '8D':
                    time_cov = '8d'
                elif m.group(3) == 'MO':
                    time_cov = '1m'

                return os.path.join(gridded_oc_prefix_path, 'contributed', 'SO-Johnson',
                                    'chl', time_cov, product_name, os.path.basename(filepath))

        else:
            raise InvalidFileNameError("file name: \"{filename}\" not matching regex to deduce dest_path".format(filename=os.path.basename(filepath)))
