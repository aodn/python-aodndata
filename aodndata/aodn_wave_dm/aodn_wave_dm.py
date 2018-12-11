from __future__ import absolute_import
from __future__ import unicode_literals
import os
import re

from netCDF4 import Dataset
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string

BOM_DIR = 'Bureau_of_Meteorology'
DOT_WA_DIR = 'Department_of_Transport-Western_Australia'
DES_QLD_DIR = 'Department_of_Environment_and_Science-Queensland'

WAVERIDER_DIR = 'Waverider_Buoys'
AWAC_DIR = 'Acoustic_Wave-Current_Profiler'
DELAYED_DIR = 'DELAYED'

DOT_WA_AWAC = re.compile(r"""
                         DOT-WA_
                         (?P<data_code>[A-Z].*)_
                         (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                         (?P<site_code>.*)_AWAC-
                         (?P<data_type>.*(TEMP|TIDE|STATUS|WAVE|CURRENT))_FV01_END-
                         (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                         """, re.VERBOSE)

DOT_WA_WAVERIDER = re.compile(r"""
                              DOT-WA_W_
                              (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                              (?P<site_code>.*)_WAVERIDER_FV01_END-                               
                              (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                              """, re.VERBOSE)

BOM_WAVERIDER = re.compile(r"""
                           BOM_W_
                           (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                           (?P<site_code>(SORELL|COUEDIC))_WAVERIDER_FV01_END-
                           (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                           """, re.VERBOSE)

DES_QLD_WAVERIDER = re.compile(r"""
                               DES-QLD_W_
                               (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                               (?P<site_code>(.*))_WAVERIDER_FV01_END-
                               (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                               """, re.VERBOSE)


def dest_path_aodn_wave_dm(filepath):
    file_basename = os.path.basename(filepath)
    with Dataset(filepath, mode='r') as nc_obj:
        site_name = nc_obj.site_name

    if BOM_WAVERIDER.match(file_basename):
        data_base_dir = os.path.join(BOM_DIR, WAVERIDER_DIR, DELAYED_DIR)
        product_dir = site_name.replace(' ', '_')

    elif DES_QLD_WAVERIDER.match(file_basename):
        data_base_dir = os.path.join(DES_QLD_DIR, WAVERIDER_DIR, DELAYED_DIR)
        fields = get_pattern_subgroups_from_string(file_basename, DES_QLD_WAVERIDER)
        product_dir = fields['site_code']

    elif DOT_WA_WAVERIDER.match(file_basename):
        data_base_dir = os.path.join(DOT_WA_DIR, WAVERIDER_DIR, DELAYED_DIR)
        fields = get_pattern_subgroups_from_string(file_basename, DOT_WA_WAVERIDER)
        product_dir = os.path.join(site_name.replace(' ', '_'), fields['site_code'])

    elif DOT_WA_AWAC.match(file_basename):
        data_base_dir = os.path.join(DOT_WA_DIR, AWAC_DIR, DELAYED_DIR)
        fields = get_pattern_subgroups_from_string(file_basename, DOT_WA_AWAC)
        product_dir = fields['site_code']

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce path".format(
                filename=file_basename))

    return os.path.join(data_base_dir, product_dir, os.path.basename(filepath))
