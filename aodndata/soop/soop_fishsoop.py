import datetime
import os
import re
from datetime import datetime

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType
from aodncore.util.misc import get_pattern_subgroups_from_string
from aodncore.pipeline.exceptions import InvalidFileNameError

FISHSOOP_FILE_PATTERN = re.compile(r"""
                              IMOS_SOOP-FishSOOP_
                              (?P<data_code>[TP]{2})_
                              (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                              (?P<qc_level>FV00|FV01)_
                              (?P<serial_number>[0-9].*)
                              \.nc$
                              """, re.VERBOSE)


class SoopFishSoopHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopFishSoopHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def process(self):
        nc_file = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        nc_file[0].publish_type = PipelineFilePublishType.UPLOAD_ONLY

    @staticmethod
    def dest_path(filepath, file_pattern=FISHSOOP_FILE_PATTERN):
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

            return os.path.join('IMOS', 'SOOP', 'SOOP-FishSOOP', data_mode,
                                str(nc_time_cov_start.year),
                                str('%02d' % nc_time_cov_start.month),
                                os.path.basename(filepath))
        else:
            raise InvalidFileNameError(
                "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                    filename=os.path.basename(filepath)))
