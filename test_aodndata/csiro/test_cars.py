from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from aodndata.csiro.cars import dest_path_cars
from aodncore.pipeline.exceptions import InvalidFileNameError

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestCarsHandler(unittest.TestCase):

    def test_dest_path_cars(self):
        good_nc = os.path.join(TEST_ROOT, 'CARS2009_World_monthly_01.nc')
        self.assertEqual(dest_path_cars(good_nc), 'CSIRO/Climatology/CARS/2009/AODN-product/CARS2009_World_monthly_01.nc')

        bad_nc = os.path.join(TEST_ROOT, 'BAD.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_cars(bad_nc)

if __name__ == '__main__':
    unittest.main()
