import os
import re
from datetime import datetime

from aodncore.util.misc import get_pattern_subgroups_from_string

from aodncore.pipeline import HandlerBase
from aodncore.pipeline.exceptions import InvalidFileNameError

L3S_L3C_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3S|L3C)_.*-AVHRR
                                (?P<sat_value>.*)_D-
                                (?P<temporal_extent>1d|3d|6d|14d|1m)_
                                (?P<day_time>day|night|dn).*\.nc$
                                """, re.VERBOSE)

L3S_MULTISENSOR_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3S)_.*-MultiSensor-
                                (?P<temporal_extent>1d|3d|6d|14d|1m)_
                                (?P<day_time>day|night|dn)
                                (?P<optional>_Southern|)
                                \.nc$
                                """, re.VERBOSE)

L3S_GEOPOLAR_MULTISENSOR_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3S)_.*-GeoPolar_MultiSensor-
                                (?P<temporal_extent>1d|3d|6d|14d|1m)_
                                (?P<day_time>day|night|dn)
                                (?P<version>-v0\d.0-fv0\d.0|)
                                \.nc$
                                """, re.VERBOSE)

L3C_HIM08_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3C)_.*-AHI_H08-
                                (?P<temporal_extent>1h|4h|1d|3d|6d|14d|1m)(_|)
                                (?P<day_time>|day|night|dn)
                                (?P<version>-v0\d.0-fv0\d.0|)
                                \.nc$
                                """, re.VERBOSE)

L3U_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3U)_.*-AVHRR
                                (?P<sat_value>[0-9].*)_D-
                                (?P<pass_direction>Asc|Des)
                                (?P<optional>_Southern|)
                                \.nc$
                                """, re.VERBOSE)

L3U_VIIRS_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3U)_.*-VIIRS_NPP.*
                                (?P<optional>_Southern|)
                                \.nc$
                                """, re.VERBOSE)

L3C_VIIRS_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L3C)_.*-VIIRS_NPP.*
                                (?P<temporal_extent>1d|3d|6d|14d|1m)_
                                (?P<day_time>day|night|dn)
                                (?P<optional>_Southern|)
                                \.nc$
                                """, re.VERBOSE)

L3P_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{8})-ABOM-
                                (?P<product_type>L3P)_.*-AVHRR_.*\.nc$
                                """, re.VERBOSE)

L4_FILE_PATTERN = re.compile(r"""
                                (?P<nc_time_cov_start>[0-9]{14})-ABOM-
                                (?P<product_type>L4)_GHRSST-SSTfnd-
                                (?P<product_name>RAMSSA|GAMSSA)_.*\.nc$
                                """, re.VERBOSE)

GHRSST_PREFIX_PATH = 'IMOS/SRS/SST/ghrsst'


def get_info_nc(filepath):
    file_basename = os.path.basename(filepath)

    if L3S_L3C_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3S_L3C_FILE_PATTERN)
        day_time = fields['day_time']
        temporal_extent = fields['temporal_extent']
    elif L3U_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3U_FILE_PATTERN)
        day_time = None
        temporal_extent = None
    elif L3S_MULTISENSOR_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3S_MULTISENSOR_FILE_PATTERN)
        day_time = fields['day_time']
        temporal_extent = fields['temporal_extent']
        fields['product_type'] = '%sM' % fields['product_type']
    elif L3S_GEOPOLAR_MULTISENSOR_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3S_GEOPOLAR_MULTISENSOR_FILE_PATTERN)
        day_time = fields['day_time']
        temporal_extent = fields['temporal_extent']
        fields['product_type'] = '%sGM' % fields['product_type']
    elif L3C_HIM08_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3C_HIM08_FILE_PATTERN)
        day_time = fields['day_time']
        temporal_extent = fields['temporal_extent']
        fields['sat_value'] = 'h08'
    elif L3U_VIIRS_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3U_VIIRS_FILE_PATTERN)
        day_time = ''
        temporal_extent = None
        fields['sat_value'] = 'snpp'
    elif L3C_VIIRS_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, L3C_VIIRS_FILE_PATTERN)
        day_time = fields['day_time']
        temporal_extent = fields['temporal_extent']
        fields['sat_value'] = 'snpp'
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))

    prod_lev = fields['product_type']

    if day_time == 'night':
        day_time = 'ngt'

    date_nc = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%d%H%M%S')

    sat_value = fields.get('sat_value', '')
    if sat_value.isdigit():
        sat_value = 'n%s' % sat_value

    if prod_lev != 'L3U':
        product_path = '%s-%s' % (prod_lev, temporal_extent)
    else:
        product_path = prod_lev

    if 'Southern' in filepath:
        if '-' in product_path:
            product_path = '%sS' % product_path
        else:
            product_path = '%s-%s' % (product_path, 'S')

    file_info = {'prod_level': prod_lev,
                 'temporal_extent': temporal_extent,
                 'day_time': day_time,
                 'date_data': date_nc,
                 'sat_value': sat_value,
                 'product_path': product_path}

    return file_info


class SrsGhrsstHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsGhrsstHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def dest_path(filepath):
        file_basename = os.path.basename(filepath)

        # remove file version from filename for Himawari and GeoPolar products
        if L3C_HIM08_FILE_PATTERN.match(file_basename) or L3S_GEOPOLAR_MULTISENSOR_FILE_PATTERN.match(file_basename):
            if L3C_HIM08_FILE_PATTERN.match(file_basename):
                fields = get_pattern_subgroups_from_string(file_basename, L3C_HIM08_FILE_PATTERN)

            elif L3S_GEOPOLAR_MULTISENSOR_FILE_PATTERN.match(file_basename):
                fields = get_pattern_subgroups_from_string(file_basename, L3S_GEOPOLAR_MULTISENSOR_FILE_PATTERN)

            version = fields['version']
            file_basename = file_basename.replace(version, '')  # remove  file version from filename

        if L3P_FILE_PATTERN.match(file_basename):
            fields = get_pattern_subgroups_from_string(file_basename, L3P_FILE_PATTERN)
            year = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%d').year
            return os.path.join(GHRSST_PREFIX_PATH, fields['product_type'], '14d',
                                str(year),
                                file_basename)

        if L4_FILE_PATTERN.match(file_basename):
            fields = get_pattern_subgroups_from_string(file_basename, L4_FILE_PATTERN)
            year = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%d%H%M%S').year
            return os.path.join(GHRSST_PREFIX_PATH, fields['product_type'], fields['product_name'],
                                str(year),
                                file_basename)

        file_info = get_info_nc(filepath)

        if file_info['sat_value'] is None:
            path = os.path.join(GHRSST_PREFIX_PATH,
                                file_info['product_path'],
                                file_info['day_time'],
                                str(file_info['date_data'].year),
                                file_basename)

        elif file_info['day_time'] is None:
            path = os.path.join(GHRSST_PREFIX_PATH,
                                file_info['product_path'],
                                file_info['sat_value'],
                                str(file_info['date_data'].year),
                                file_basename)

        else:
            path = os.path.join(GHRSST_PREFIX_PATH,
                                file_info['product_path'],
                                file_info['day_time'],
                                file_info['sat_value'],
                                str(file_info['date_data'].year),
                                file_basename)

        return path
