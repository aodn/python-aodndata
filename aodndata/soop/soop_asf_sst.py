from __future__ import absolute_import
from __future__ import unicode_literals
import os

from aodncore.pipeline import HandlerBase
from aodncore.pipeline.exceptions import InvalidFileFormatError

from .ship_callsign import ship_callsign_list


class SoopAsfSstHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopAsfSstHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']
        self.ships = ship_callsign_list()
        self.data_codes = {'FMT': 'flux_product',
                           'MT': 'meteorological_sst_observations'}

    def dest_path(self, filepath):
        """
        # eg file IMOS_SOOP-SST_T_20081230T000900Z_VHW5167_FV01.nc
        # IMOS_SOOP-ASF_MT_20150913T000000Z_ZMFR_FV01_C-20150914T042207Z.nc
        # IMOS_<Facility-Code>_<Data-Code>_<Start-date>_<Platform-Code>_FV<File-Version>_<Product-Type>_END-<End-date>_C-<Creation_date>_<PARTX>.nc
        """
        filepath = os.path.basename(filepath)
        file_parts = filepath.split("_")

        # the file name must have at least 6 component parts to be valid
        if len(file_parts) > 5:
            facility = file_parts[1]  # <Facility-Code>
            year = file_parts[3][:4]  # year out of <Start-date>

            # check for the code in the ships
            code = file_parts[4]
            if code in self.ships:
                platform = code + "_" + self.ships[code]

                if facility == "SOOP-ASF":
                    if 'ISAR-QC' in file_parts and file_parts[2] in self.data_codes:
                        product = self.data_codes[file_parts[2]]
                        target_dir = os.path.join('IMOS', 'SOOP', facility, platform, product, year, 'ISAR-QC')
                        return os.path.join(target_dir, filepath)

                    if file_parts[2] in self.data_codes:
                        product = self.data_codes[file_parts[2]]
                        target_dir = os.path.join('IMOS', 'SOOP', facility, platform, product, year)
                        return os.path.join(target_dir, filepath)

                    else:
                        raise InvalidFileFormatError(
                            "Hierarchy not created for '{name}'".format(name=filepath)
                        )

                        return None

                else:
                    # soop sst
                    target_dir = os.path.join('IMOS', 'SOOP', facility, platform, year)

                    # files that contain '1-min-avg.nc' get their own sub folder
                    if "1-min-avg" in filepath:
                        target_dir = os.path.join(target_dir, "1-min-avg")

                    return os.path.join(target_dir, filepath)
