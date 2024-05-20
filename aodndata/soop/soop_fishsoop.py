import datetime
import os
import re
import tempfile
from datetime import datetime

import matplotlib.pyplot as plt
from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType
from aodncore.util.misc import get_pattern_subgroups_from_string
from netCDF4 import Dataset
from numpy import ma

FISHSOOP_FILE_PATTERN = re.compile(r"""
                              IMOS_SOOP-FishSOOP_T_
                              (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                              (?P<qc_level>FV00|FV01)_
                              (?P<serial_number>[0-9].*)
                              \.nc$
                              """, re.VERBOSE)


def dest_path_soop_fishsoop(filepath, file_pattern=FISHSOOP_FILE_PATTERN):
    file_basename = os.path.basename(filepath)
    if file_pattern.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, file_pattern)
        nc_time_cov_start = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ')

        qc_level = fields['qc_level']
        serial_number = fields['serial_number']

        if qc_level == 'FV00':
            data_mode = 'REALTIME'
        elif qc_level == 'FV01':
            data_mode = "DELAYED"
        else:
            return ValueError(f"{qc_level} not matching expected qc_level")

        return os.path.join('IMOS', 'SOOP', 'SOOP-FishSoop', data_mode, str(serial_number),
                            str(nc_time_cov_start.year),
                            str('%02d' % nc_time_cov_start.month),
                            os.path.basename(filepath))
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))
