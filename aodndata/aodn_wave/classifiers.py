import os
import re

from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import (InvalidFileContentError, InvalidFileNameError, InvalidFileFormatError,
                                          InvalidInputFileError)
from aodncore.pipeline import HandlerBase, PipelineFilePublishType
from aodncore.util.misc import get_pattern_subgroups_from_string


class AodnWaveFileClassifier(FileClassifier):
    """Classifier for Integral wave parameters files Delayed mode or Realtime
    """

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
    WAVE_PARAMETERS_DIR = 'Wave-parameters'
    SPECTRA_DIR = 'Spectra'
    RAW_DISPLACEMENTS_DIR = 'Raw-displacements'

    DATA_MODE_REGEX = re.compile(r"""
                               (.*)_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_
                               (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

    DATA_TYPE_REGEX = re.compile(r"""
                               (.*)_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_
                               (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

    BOM_WAVEBUOY = re.compile(r"""
                               BOM_
                               (?P<nc_time_cov_start>[0-9]{8})_
                               (?P<site_name>(.*))_(?P<mode>RT|DM)_
                               (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                               (?P<nc_time_cov_end>[0-9]{8})\.nc$
                               """, re.VERBOSE)

    DOT_WA_WAVEBUOY = re.compile(r"""
                                  DOT-WA_
                                  (?P<nc_time_cov_start>[0-9]{8})_
                                  (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                  (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-                               
                                  (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                  """, re.VERBOSE)

    DTA_NZ_WAVEBUOY = re.compile(r"""
                                  DTA_
                                  (?P<nc_time_cov_start>[0-9]{8})_
                                  (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                  (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-                               
                                  (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                  """, re.VERBOSE)

    DES_QLD_WAVEBUOY = re.compile(r"""
                                   DES-QLD_
                                   (?P<nc_time_cov_start>[0-9]{8})_
                                   (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                   (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                                   (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                   """, re.VERBOSE)

    MHL_WAVEBUOY = re.compile(r"""
                                   IMOS_ANMN-NSW_
                                   (?P<nc_time_cov_start>[0-9]{8})_
                                   (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                   (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                                   (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                   """, re.VERBOSE)

    NTP_WAVEBUOY = re.compile(r"""
                                   IMOS_NTP-WAVE_
                                   (?P<nc_time_cov_start>[0-9]{8})_
                                   (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                   (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                                   (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                   """, re.VERBOSE)

    NSW_DPE_WAVEBUOY = re.compile(r"""
                                   NSW-DPE_
                                   (?P<nc_time_cov_start>[0-9]{8})_
                                   (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                   (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                                   (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                   """, re.VERBOSE)

    VIC_DEAKIN_WAVEBUOY = re.compile(r"""
                                   VIC-DEAKIN-UNI_
                                   (?P<nc_time_cov_start>[0-9]{8})_
                                   (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                   (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                                   (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                   """, re.VERBOSE)

    UWA_WAVEBUOY = re.compile(r"""
                                   UWA_
                                   (?P<nc_time_cov_start>[0-9]{8})_
                                   (?P<site_name>(.*))_(?P<mode>RT|DM)_
                                   (?P<datatype>WAVE-PARAMETERS|SPECTRA|RAW-DISPLACEMENTS)_END-
                                   (?P<nc_time_cov_end>[0-9]{8})\.nc$
                                   """, re.VERBOSE)

    @classmethod
    def dest_path_aodn_wave(cls, filepath):
        file_basename = os.path.basename(filepath)

        fields = get_pattern_subgroups_from_string(file_basename, cls.DATA_MODE_REGEX)
        mode = fields['mode']
        if mode == 'RT':
            mode_dir = cls.REALTIME_DIR
        elif mode == 'DM':
            mode_dir = cls.DELAYED_DIR
        else:
            raise InvalidFileNameError(
                "file name: \"{filename}\" data mode (RT/DM) missing or incorrect".format(
                    filename=file_basename))

        fields = get_pattern_subgroups_from_string(file_basename, cls.DATA_TYPE_REGEX)
        datatype = fields['datatype']
        if datatype == 'WAVE-PARAMETERS':
            datatype_dir = cls.WAVE_PARAMETERS_DIR
        elif datatype == 'SPECTRA':
            datatype_dir = cls.SPECTRA_DIR
        elif datatype == 'RAW-DISPLACEMENTS':
            datatype_dir = cls.RAW_DISPLACEMENTS_DIR
        else:
            raise InvalidFileNameError(
                "file name: \"{filename}\" wave data type (wave parameters/spectra/raw displacements) "
                "missing or incorrect".format(
                    filename=file_basename))

        if cls.BOM_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.BOM_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.BOM_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.DOT_WA_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.DOT_WA_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.DOT_WA_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.DTA_NZ_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.DTA_NZ_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.DTA_NZ_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.DES_QLD_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.DES_QLD_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.DES_QLD_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.MHL_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.NSW_DPE_DIR, cls.MHL_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.MHL_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.NTP_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.NTP_WAVE_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.NTP_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.NSW_DPE_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.NSW_DPE_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.NSW_DPE_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.VIC_DEAKIN_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.VIC_DEAKIN_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.VIC_DEAKIN_WAVEBUOY)
            product_dir = fields['site_name']

        elif cls.UWA_WAVEBUOY.match(file_basename):
            data_base_dir = os.path.join(cls.UWA_DIR, cls.WAVEBUOY_DIR, mode_dir, datatype_dir)
            fields = get_pattern_subgroups_from_string(file_basename, cls.UWA_WAVEBUOY)
            product_dir = fields['site_name']

        else:
            raise InvalidFileNameError(
                "file name: \"{filename}\" not matching regex to deduce path".format(
                    filename=file_basename))

        return os.path.join(data_base_dir, product_dir, os.path.basename(filepath))

    @classmethod
    def get_data_type(cls, filepath):
        file_basename = os.path.basename(filepath)

        fields = get_pattern_subgroups_from_string(file_basename, cls.DATA_TYPE_REGEX)
        datatype = fields['datatype']

        """ work out data type from filename
        if WAVE-PARAMETERS (to harvest)
        or if SPECTRA|RAW-DISPLACEMENTS (to only upload) """
        if re.match(datatype, 'WAVE-PARAMETERS', file_basename):
            file_basename.publish_type = PipelineFilePublishType.HARVEST_ONLY
        elif re.match(datatype, 'SPECTRA', file_basename):
            file_basename.publish_type = PipelineFilePublishType.UPLOAD_ONLY
        elif re.match(datatype, 'RAW-DISPLACEMENTS', file_basename):
            file_basename.publish_type = PipelineFilePublishType.UPLOAD_ONLY
        else:
            raise InvalidFileNameError(
                "Invalid filename, the data type {datatype} is not part of wave dataset ".format(datatype=cls.datatype))

