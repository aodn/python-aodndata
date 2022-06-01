import os
import re

from netCDF4 import Dataset
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodncore.util.misc import get_pattern_subgroups_from_string

BOM_DIR = 'Bureau_of_Meteorology'
DOT_WA_DIR = 'Department_of_Transport-Western_Australia'
DTA_NZ_DIR = 'Defence_Technology_Agency-New_Zealand'
DES_QLD_DIR = 'Department_of_Environment_and_Science-Queensland'
MHL_DIR = 'Manly_Hydraulics_Laboratory'
NTP_WAVE_DIR = 'IMOS/NTP/Low_Cost_Wave_Buoy_Technology'
NSW_DPE_DIR = 'Department_of_Planning_and_Environment-New_South_Wales'
VIC_DEAKIN_DIR = 'Deakin_University'
UWA_DIR = 'UWA'

WAVEBUOY_DIR = 'Wave_Buoys'
DELAYED_DIR = 'Delayed'
REALTIME_DIR = 'Realtime'

DATA_MODE_REGEX = re.compile(r"""
                           (.*)_
                           (?P<nc_time_cov_start>[0-9]{8})_
                           (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                           (?P<nc_time_cov_end>[0-9]{8})\.nc$
                           """, re.VERBOSE)

BOM_WAVEBUOY = re.compile(r"""
                           BOM_
                           (?P<nc_time_cov_start>[0-9]{8})_
                           (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                           (?P<nc_time_cov_end>[0-9]{8})\.nc$
                           """, re.VERBOSE)

DOT_WA_WAVEBUOY = re.compile(r"""
                              DOT-WA_
                              (?P<nc_time_cov_start>[0-9]{8})_
                              (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-                               
                              (?P<nc_time_cov_end>[0-9]{8})\.nc$
                              """, re.VERBOSE)

DTA_NZ_WAVEBUOY = re.compile(r"""
                              DTA_
                              (?P<nc_time_cov_start>[0-9]{8})_
                              (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-                               
                              (?P<nc_time_cov_end>[0-9]{8})\.nc$
                              """, re.VERBOSE)

DES_QLD_WAVEBUOY = re.compile(r"""
                               DES-QLD_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

MHL_WAVEBUOY = re.compile(r"""
                               IMOS_ANMN-NSW_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

NTP_WAVEBUOY = re.compile(r"""
                               IMOS_NTP-WAVE_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

NSW_DPE_WAVEBUOY =  re.compile(r"""
                               NSW-DPE_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

VIC_DEAKIN_WAVEBUOY =  re.compile(r"""
                               VIC-DEAKIN-UNI_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

UWA_WAVEBUOY = re.compile(r"""
                               UWA_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_WAVE-PARAMETERS_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

def dest_path_aodn_wave(filepath):
    file_basename = os.path.basename(filepath)

    fields = get_pattern_subgroups_from_string(file_basename, DATA_MODE_REGEX)
    mode = fields['mode']
    if mode == 'RT':
        mode_dir = REALTIME_DIR
    elif mode == 'DM':
        mode_dir = DELAYED_DIR
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" data mode (RT/DM) missing or incorrect".format(
                filename=file_basename))

    if BOM_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(BOM_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, BOM_WAVEBUOY)
        product_dir = fields['site_name']

    elif DOT_WA_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(DOT_WA_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, DOT_WA_WAVEBUOY)
        product_dir = fields['site_name']

    elif DTA_NZ_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(DTA_NZ_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, DTA_NZ_WAVEBUOY)
        product_dir = fields['site_name']

    elif DES_QLD_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(DES_QLD_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, DES_QLD_WAVEBUOY)
        product_dir = fields['site_name']

    elif MHL_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(NSW_DPE_DIR, MHL_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, MHL_WAVEBUOY)
        product_dir = fields['site_name']

    elif NTP_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(NTP_WAVE_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, NTP_WAVEBUOY)
        product_dir = fields['site_name']

    elif NSW_DPE_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(NSW_DPE_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, NSW_DPE_WAVEBUOY)
        product_dir = fields['site_name']

    elif VIC_DEAKIN_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(VIC_DEAKIN_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, VIC_DEAKIN_WAVEBUOY)
        product_dir = fields['site_name']

    elif UWA_WAVEBUOY.match(file_basename):
        data_base_dir = os.path.join(UWA_DIR, WAVEBUOY_DIR, mode_dir)
        fields = get_pattern_subgroups_from_string(file_basename, UWA_WAVEBUOY)
        product_dir = fields['site_name']

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce path".format(
                filename=file_basename))

    return os.path.join(data_base_dir, product_dir, os.path.basename(filepath))
