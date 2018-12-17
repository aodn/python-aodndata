import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string

PREFIX_PATH = 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00'
VALID_SATS = ["CRYOSAT-2",
              "ENVISAT",
              "ERS-1",
              "ERS-2",
              "GEOSAT",
              "GFO",
              "HY-2",
              "JASON-1",
              "JASON-2",
              "JASON-3",
              "SARAL",
              "SENTINEL-3",
              "TOPEX"]


def dest_path_srs_surface_waves(filepath):
    platforms = '|'.join(VALID_SATS)

    FILE_PATTERN = re.compile(r"""
                                IMOS_SRS-Surface-Waves_MW_
                                (?P<platform_code>{})_FV02_
                                (?P<latitude>[0-9]{{3}})
                                (?P<latitude_dir>(S|N))-
                                (?P<longitude>[0-9]{{3}})E-
                                DM00\.nc$
                                """.format(platforms), re.VERBOSE)

    file_basename = os.path.basename(filepath)
    if FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, FILE_PATTERN)
        lat = int(fields['latitude'])
        lon = int(fields['longitude'])
        lat_dir = fields['latitude_dir']

        def round_down_div_10(val, divisor=10):
            """ return div 10 rounded value of a value"""
            return val - (val % divisor)

        if lat_dir == 'S':
            lat_bottom_left = round_down_div_10(lat) + 10
        elif lat_dir == 'N':
            lat_bottom_left = round_down_div_10(lat)

        lon_bottom_left = round_down_div_10(lon)

        coord_dirname = '{lat_bottom_left}{lat_dir}_{lon_bottom_left}E'.format(
            lat_bottom_left=str(lat_bottom_left).zfill(3),
            lon_bottom_left=str(lon_bottom_left).zfill(3),
            lat_dir=lat_dir)

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))

    return os.path.join(PREFIX_PATH, fields['platform_code'], coord_dirname, file_basename)


