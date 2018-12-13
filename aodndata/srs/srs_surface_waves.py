import os
import re

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string
from aodncore.pipeline import HandlerBase

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


class SrsSurfaceWavesHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsSurfaceWavesHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.dir_manifest']
        self.resolve_params = {'relative_path_root': os.path.join(self._config.pipeline_config['global']['wip_dir'])}

    @staticmethod
    def dest_path(filepath):
        platforms = '|'.join(VALID_SATS)

        FILE_PATTERN = re.compile(r"""
                                    IMOS_SRS-Surface-Waves_MW_
                                    (?P<platform_code>{})_FV02_
                                    (?P<latitude>[0-9]{{3}})(S|N)-
                                    (?P<longitude>[0-9]{{3}})E-
                                    DM00\.nc$
                                    """.format(platforms), re.VERBOSE)

        file_basename = os.path.basename(filepath)
        if FILE_PATTERN.match(file_basename):
            fields = get_pattern_subgroups_from_string(file_basename, FILE_PATTERN)
        else:
            raise InvalidFileNameError(
                "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                    filename=os.path.basename(filepath)))

        return os.path.join(PREFIX_PATH, fields['platform_code'], file_basename)
