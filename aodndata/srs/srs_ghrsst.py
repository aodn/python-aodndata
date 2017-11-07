import os
import re
from datetime import datetime

from aodncore.pipeline import HandlerBase


class SrsGhrsstHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsGhrsstHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def get_info_nc(filepath):

        if 'L3S' in os.path.basename(filepath) or 'L3C' in os.path.basename(filepath):
            info_re = re.compile(
                r'^([0-9]{14})-ABOM-(L3S|L3C)_.*-AVHRR(.*)_D-(1d|3d|6d|14d|1m)_(day|night|dn).*.nc$')
            info_re_match = info_re.findall(os.path.basename(filepath))[0]
            day_time = info_re_match[4]

        elif 'L3U' in os.path.basename(filepath):
            info_re = re.compile(
                r'^([0-9]{14})-ABOM-(L3U)_.*-AVHRR(.*)_D-(Asc|Des)(.*Southern)?.nc$')
            info_re_match = info_re.findall(os.path.basename(filepath))[0]
            day_time = None

        prod_lev = info_re_match[1]
        temporal_extent = info_re_match[3]

        if day_time == 'night':
            day_time = 'ngt'

        date_nc = datetime.strptime(info_re_match[0], '%Y%m%d%H%M%S')

        sat_number = info_re_match[2]
        if sat_number == '':
            sat_number = None

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
                     'sat_number': sat_number,
                     'product_path': product_path}

        return file_info

    @staticmethod
    def dest_path(filepath):
        ghrsst_prefix_path = 'IMOS/SRS/SST/ghrsst'

        if 'L3P' in filepath:
            return os.path.join(ghrsst_prefix_path, 'L3P', '14d', os.path.basename(filepath)[0:4],
                                os.path.basename(filepath))

        file_info = SrsGhrsstHandler.get_info_nc(filepath)

        if file_info['sat_number'] is None:
            path = os.path.join(ghrsst_prefix_path,
                                file_info['product_path'],
                                file_info['day_time'],
                                str(file_info['date_data'].year),
                                os.path.basename(filepath))

        elif file_info['day_time'] is None:
            path = os.path.join(ghrsst_prefix_path,
                                file_info['product_path'],
                                'n%s' % file_info['sat_number'],
                                str(file_info['date_data'].year),
                                os.path.basename(filepath))

        else:
            path = os.path.join(ghrsst_prefix_path,
                                file_info['product_path'],
                                file_info['day_time'],
                                'n%s' % file_info['sat_number'],
                                str(file_info['date_data'].year),
                                os.path.basename(filepath))

        return path
