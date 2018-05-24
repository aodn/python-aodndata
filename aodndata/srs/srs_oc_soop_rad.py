import os
import re

from aodncore.pipeline import HandlerBase
from aodndata.soop.ship_callsign import ship_callsign_list
from aodncore.pipeline.exceptions import InvalidFileNameError


class SrsOcSoopRadHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsOcSoopRadHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']
        self.ships = ship_callsign_list()

    @staticmethod
    def dest_path(filepath):
        filepath = re.sub('_C-.*$', '.nc', filepath)  # strip creation date from filepath if exists
        netcdf_filename = os.path.basename(filepath)
        m = re.search('^IMOS_SRS-OC_F_([0-9]{8}T[0-9]{6}Z)_(.*)_FV0([0-2]{1})_DALEC_.*\.nc$', netcdf_filename)

        if m is None:
            raise InvalidFileNameError("file name not matching regex to deduce dest_path")

        platform_code = m.group(2)
        file_version_code = 'FV0%s' % m.group(3)

        ships_dic = ship_callsign_list()

        if platform_code in ships_dic:
            vessel_name = ships_dic[platform_code]
        else:
            raise InvalidFileNameError(
                "Vessel name not known '{name}'".format(name=platform_code))

        if not (file_version_code != "FV00" or file_version_code != "FV01" or file_version_code != "FV02" ):
            raise InvalidFileNameError(
                "File_version code is unknown for '{name}'".format(name=filepath))

        year = m.group(1)[0:4]
        relative_netcdf_path = os.path.join('IMOS', 'SRS', 'OC', 'radiometer', '%s_%s' % (platform_code, vessel_name),
                                            year)

        if file_version_code == "FV02":
            relative_netcdf_path = os.path.join(relative_netcdf_path, 'fv02-products', netcdf_filename)
        else:
            relative_netcdf_path = os.path.join(relative_netcdf_path, netcdf_filename)

        return relative_netcdf_path
