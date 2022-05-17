import os
import re

from netCDF4 import Dataset
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError

BOM_DIR = 'Bureau_of_Meteorology'
DOT_WA_DIR = 'Department_of_Transport-Western_Australia'
DTA_NZ_DIR = 'Defence_Technology_Agency-New_Zealand'
DES_QLD_DIR = 'Department_of_Environment_and_Science-Queensland'
NTP_WAVE_DIR = 'IMOS/NTP/Low_Cost_Wave_Buoy_Technology'
MHL_DIR_BASE = 'NSW-OEH'
MHL_DIR = 'Manly_Hydraulics_Laboratory'
MHL_WAVERIDER_DIR = 'Wave'
WAVEBUOY_DIR = 'Wave_Buoys'

DELAYED_DIR = 'DELAYED'
REALTIME_DIR = 'REALTIME'
def dest_path_aodn_wave(filepath):
    file_basename = os.path.basename(filepath)
    with Dataset(filepath, mode='r') as nc_obj:
        site_name = nc_obj.site_name

