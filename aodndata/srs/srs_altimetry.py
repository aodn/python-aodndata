import os

from aodncore.pipeline import HandlerBase
from netCDF4 import Dataset


class SrsAltHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsAltHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def dest_path(filepath):
        srs_alt_dir = os.path.join('IMOS', 'SRS', 'ALTIMETRY', 'calibration_validation')
        with Dataset(filepath, mode='r') as n:
            site_code = n.site_code
            instrument = n.instrument

        if instrument == 'SBE37':
            product_type = 'CTD_timeseries'
        elif instrument == 'SBE26':
            product_type = 'Pressure_gauge'
        elif instrument == 'Aquad':
            product_type = 'Velocity'
        elif instrument == 'ST_CM':
            product_type = 'Velocity'
        else:
            raise ValueError("unknown instrument '{instrument}'".format(instrument=instrument))

        return os.path.join(srs_alt_dir, site_code, product_type,
                            os.path.basename(filepath))
