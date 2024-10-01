import os
import unittest

from netCDF4 import Dataset
import numpy as np
from numpy import ma

from aodncore.testlib.basetest import BaseTestCase

from aodndata.moorings.burst_average import create_burst_average_netcdf

TEST_ROOT = os.path.dirname(__file__)
INPUT_FILE = os.path.join(
    TEST_ROOT,
    'IMOS_ANMN-NRS_BCKOSTUZ_20081120T081531Z_NRSROT_FV01_NRSROT-0811-WQM-21_END-20081120T171535Z_C-20190418T000000Z.nc'
)

INPUT_DEPTH_ALL_BAD_FLAG_FILE = os.path.join(
    TEST_ROOT,
    'IMOS_ANMN-NRS_FZ_20170929T003418Z_NRSYON_FV01_NRSYON-1709-SRF-ECO-PARSB-1.1_END-20180509T233213Z_C-20190308T030455Z.nc'
)


STATS = dict(TEMP=ma.masked_values([-999, -999, -999, -999,  4.,  5., 11., 17.], -999),
             TEMP_num_obs=ma.array([0,  0,  0,  0, 61, 61, 11, 21]),
             TEMP_burst_max=ma.masked_values([-999, -999, -999, -999,  4.,  5., 16., 27.], -999),
             TEMP_burst_min=ma.masked_values([-999, -999, -999, -999,  4.,  5.,  6.,  7.], -999),
             TEMP_burst_sd=ma.masked_values([-999, -999, -999, -999, 0.0, 0.0, 3.1622776601683795, 6.0553007081949835],
                                            -999)
             )
N_COMP = len(STATS['TEMP'])


class TestBurstAverage(BaseTestCase):
    def test_burst_average(self):
        averaged_file = create_burst_average_netcdf(INPUT_FILE, self.temp_dir)
        ds = Dataset(averaged_file)
        for var, values in STATS.items():
            self.assertTrue(np.isclose(values, ds.variables[var][:N_COMP]).all())

    def test_burst_average_bad_flag(self):
        """
        testing burst code with input NetCDF containing all bad qc flags for the Depth variable
        """
        averaged_file = create_burst_average_netcdf(INPUT_DEPTH_ALL_BAD_FLAG_FILE, self.temp_dir)
        ds = Dataset(averaged_file)
        self.assertTrue('DEPTH' not in ds.variables)  # depth variable removed from dataset since only containing NaNs


if __name__ == '__main__':
    unittest.main()
