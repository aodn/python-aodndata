import os
import unittest

from aodndata.csiro.sstaars import dest_path_sstaars
from aodncore.pipeline.exceptions import InvalidFileNameError

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSstaarsHandler(unittest.TestCase):

    def test_dest_path_sstaars(self):
        good_nc = os.path.join(TEST_ROOT, 'SSTAARS.nc')
        self.assertEqual(dest_path_sstaars(good_nc), 'CSIRO/Climatology/SSTAARS/2017/SSTAARS.nc')

        good_nc_daily = os.path.join(TEST_ROOT, 'SSTAARS_daily_fit_001.nc')
        self.assertEqual(dest_path_sstaars(good_nc_daily), 'CSIRO/Climatology/SSTAARS/2017/AODN-product/SSTAARS_daily_fit_001.nc')

        bad_nc = os.path.join(TEST_ROOT, 'BAD.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_sstaars(bad_nc)

if __name__ == '__main__':
    unittest.main()
