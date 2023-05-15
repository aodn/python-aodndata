import os
import re
from datetime import datetime

from aodncore.pipeline import HandlerBase
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string

SRS_OC_GRIDDED_VARIABLES = ['chl_gsm', 'chl_oc3', 'chl_oci', 'chl_oc4', 'chl_carder', 'dt', 'ipar', 'K_490', 'l2_flags',
                               'nanop_brewin2010at', 'nanop_brewin2012in', 'npp_vgpm_eppley_gsm',
                               'npp_vgpm_eppley_oc3', 'npp_vgpm_eppley_oc4', 'owtd_csiro', 'par', 'picop_brewin2010at',
                               'picop_brewin2012in', 'sst', 'sst_quality', 'tsm_clark16', 'tsm_clark']

OC_VARIABLES = '|'.join(SRS_OC_GRIDDED_VARIABLES)
OC_GRIDDED_PREFIX_PATH = 'IMOS/SRS/OC/gridded'

RJOHNSON_FILE_PATTERN = re.compile(r"""
                                (?P<data_parameter_code>A|S)
                                (?P<nc_time_cov_start>[0-9]{14})\.L3m_
                                (?P<time_coverage_resolution>8D|MO)_
                                SO_Chl_9km\.Johnson_SO_Chl\.nc$
                                """, re.VERBOSE)

IMOS_OC_FILE_PATTERN = re.compile(r"""
                                (?P<data_parameter_code>A|S|J|V)\.
                                (?P<time_coverage_resolution>P1D|P1H)\.
                                (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)\.
                                (?P<sat_pass>aust|overpass)\.
                                (?P<oc_variable>%s)\.nc$
                                """ % OC_VARIABLES, re.VERBOSE)


class SrsOcGriddedHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsOcGriddedHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def dest_path(filepath):
        file_basename = os.path.basename(filepath)

        # NON CONTRIBUTED DATA SET
        if IMOS_OC_FILE_PATTERN.match(file_basename):
            fields = get_pattern_subgroups_from_string(file_basename, IMOS_OC_FILE_PATTERN)
            nc_time_cov_start = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ')
            data_parameter_code = fields['data_parameter_code']

            if data_parameter_code == 'A':
                product_name = 'aqua'
            elif data_parameter_code == 'S':
                product_name = 'seawifs'
            elif data_parameter_code == 'V':
                product_name = 'snpp'
            elif data_parameter_code == 'J':
                product_name = 'noaa20'

            path = os.path.join(OC_GRIDDED_PREFIX_PATH, product_name, fields['time_coverage_resolution'],
                                '%d' % nc_time_cov_start.year, '%02d' % nc_time_cov_start.month,
                                file_basename)
            return path

        # CONTRIBUTED DATA SET
        elif RJOHNSON_FILE_PATTERN.match(file_basename):
            fields = get_pattern_subgroups_from_string(file_basename, RJOHNSON_FILE_PATTERN)
            data_parameter_code = fields['data_parameter_code']
            time_coverage_resolution = fields['time_coverage_resolution']

            if data_parameter_code == 'A':
                product_name = 'aqua'
            elif data_parameter_code == 'S':
                product_name = 'seawifs'

            if time_coverage_resolution == '8D':
                time_cov = '8d'
            elif time_coverage_resolution == 'MO':
                time_cov = '1m'

            return os.path.join(OC_GRIDDED_PREFIX_PATH, 'contributed', 'SO-Johnson',
                                'chl', time_cov, product_name, file_basename)

        else:
            raise InvalidFileNameError("file name: \"{filename}\" not matching regex to deduce dest_path".
                                       format(filename=file_basename))
