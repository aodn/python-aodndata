import os
import re

from netCDF4 import Dataset
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodncore.util.misc import get_pattern_subgroups_from_string

BOM_DIR = 'Bureau_of_Meteorology'
DOT_WA_DIR = 'Department_of_Transport-Western_Australia'
DTA_NZ_DIR = 'Defence_Technology_Agency-New_Zealand'
DES_QLD_DIR = 'DES-QLD'
NTP_WAVE_DIR = 'IMOS/NTP/Low_Cost_Wave_Buoy_Technology'
MHL_DIR_BASE = 'NSW-OEH'
MHL_DIR = 'Manly_Hydraulics_Laboratory'
MHL_WAVERIDER_DIR = 'Wave'
WAVEBUOY_DIR = 'Wave_Buoys'
NSW_DPE_DIR = 'NSW-DPE'

DELAYED_DIR = 'DM'
REALTIME_DIR = 'REALTIME'

DES_QLD_WAVEBUOY = re.compile(r"""
                               DES-QLD_
                               (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                               (?P<site_name>(.*))_DM_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                               """, re.VERBOSE)

NSW_DPE_WAVEBUOY =  re.compile(r"""
                               NSW-DPE_
                               (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                               (?P<site_name>(.*))_DM_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                               """, re.VERBOSE)


def dest_path_aodn_wave_dm(filepath):
    file_basename = os.path.basename(filepath)
    with Dataset(filepath, mode='r') as nc_obj:
        site_name = nc_obj.site_name

    if DES_QLD_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(DES_QLD_DIR, WAVEBUOY_DIR, DELAYED_DIR)
        fields = get_pattern_subgroups_from_string(file_basename, DES_QLD_WAVEBUOY)
        product_dir = fields['site_name']

    elif NSW_DPE_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(NSW_DPE_DIR, WAVEBUOY_DIR, DELAYED_DIR)
        if len(site_name) == 0:
            raise InvalidFileContentError(
                "file name: \"{filename}\"; global attribute site_name is empty".format(filename=file_basename))
        product_dir = site_name

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce path".format(
                filename=file_basename))

    return os.path.join(data_base_dir, product_dir, os.path.basename(filepath))
