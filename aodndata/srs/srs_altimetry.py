import os

from aodncore.pipeline import HandlerBase
from netCDF4 import Dataset


class SrsAltHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsAltHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def dest_path(self, filepath):
        srs_alt_dir = os.path.join('IMOS', 'SRS', 'ALTIMETRY', 'calibration_validation')
        netcdf_file_obj = Dataset(filepath, mode='r')
        site_code = netcdf_file_obj.site_code
        instrument = netcdf_file_obj.instrument
        netcdf_file_obj.close()

        if instrument == 'SBE37':
            product_type = 'CTD_timeseries'
        elif instrument == 'SBE26':
            product_type = 'Pressure_gauge'
        elif instrument == 'Aquad':
            product_type = 'Velocity'
        else:
            return None

        return os.path.join(srs_alt_dir, site_code, product_type,
                            os.path.basename(filepath))
