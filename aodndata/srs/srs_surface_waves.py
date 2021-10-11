import os
import re
from datetime import datetime

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string

ALTI_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00'
ALTI_VALID_SATS = ["CRYOSAT-2",
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
                   "SENTINEL-3A",
                   "SENTINEL-3B",
                   "TOPEX"
                   ]
ALTI_FILE_PATTERN = re.compile(r"""
                            IMOS_SRS-Surface-Waves_MW_
                            (?P<platform_code>{})_FV02_
                            (?P<latitude>[0-9]{{3}})
                            (?P<latitude_dir>(S|N))-
                            (?P<longitude>[0-9]{{3}})E-
                            DM00\.nc$
                            """.format('|'.join(ALTI_VALID_SATS)), re.VERBOSE)

SCAT_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/Wind-Scatterometry-DM00'
SCAT_VALID_SATS = ["ERS-1",
                   "ERS-2",
                   "QUIKSCAT",
                   "METOP-A",
                   "OCEANSAT-2",
                   "METOP-B",
                   "METOP-C",
                   "RAPIDSCAT"
                   ]
SCAT_FILE_PATTERN = re.compile(r"""
                            IMOS_SRS-Surface-Waves_M_Wind-
                            (?P<platform_code>{})_FV02_
                            (?P<latitude>[0-9]{{3}})
                            (?P<latitude_dir>(S|N))-
                            (?P<longitude>[0-9]{{3}})E-
                            DM00\.nc$
                            """.format('|'.join(SCAT_VALID_SATS)), re.VERBOSE)

SAR_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/SAR'

SAR_FILE_PATTERN = re.compile(r"""
                              IMOS_SRS-Surface-Waves_W_
                              (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                              (?P<platform_code>Sentinel-1A|Sentinel-1B)_
                              (?P<qc_level>FV00|FV01_DM00)_
                              (?P<wavenum>K1|K2)_END-
                              (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                              """, re.VERBOSE)


def dest_path_srs_surface_waves(filepath):
    file_basename = os.path.basename(filepath)
    if ALTI_FILE_PATTERN.match(file_basename):
        return dest_path_alt_scat_common(filepath, ALTI_FILE_PATTERN, ALTI_PREFIX_PATH)
    elif SCAT_FILE_PATTERN.match(file_basename):
        return dest_path_alt_scat_common(filepath, SCAT_FILE_PATTERN, SCAT_PREFIX_PATH)
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))


def dest_path_alt_scat_common(filepath, file_pattern, prefix_path):
    file_basename = os.path.basename(filepath)
    if file_pattern.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, file_pattern)
        lat = int(fields['latitude'])
        lon = int(fields['longitude'])
        lat_dir = fields['latitude_dir']

        def round_down_div(val, divisor=20):
            """ return div rounded value of a value"""
            return val - (val % divisor)

        if lat_dir == 'S':
            lat_bottom_left = round_down_div(lat) + 20
        elif lat_dir == 'N':
            lat_bottom_left = round_down_div(lat)

        lon_bottom_left = round_down_div(lon)

        coord_dirname = '{lat_bottom_left}{lat_dir}_{lon_bottom_left}E'.format(
            lat_bottom_left=str(lat_bottom_left).zfill(3),
            lon_bottom_left=str(lon_bottom_left).zfill(3),
            lat_dir=lat_dir)

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))

    return os.path.join(prefix_path, fields['platform_code'], coord_dirname, file_basename)


def dest_path_srs_surface_waves_sar(filepath, file_pattern=SAR_FILE_PATTERN, prefix_path=SAR_PREFIX_PATH):
    file_basename = os.path.basename(filepath)
    if file_pattern.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, file_pattern)
        sat = fields['platform_code']
        qc_level = fields['qc_level']
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))

    if "FV00" in qc_level:
        qc_level_str = "REALTIME"
    elif "FV01" in qc_level:
         qc_level_str = "DELAYED"

    nc_time_cov_start = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ')

    path = os.path.join(prefix_path,qc_level_str, sat.upper(),
                        '%d' % nc_time_cov_start.year, '%02d' % nc_time_cov_start.month,
                        file_basename)
    return path
