import os
import unittest

from aodndata.deakin.deakin_bathymetry import dest_path_deakin_bathymetry

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestDeakinBathyHandler(unittest.TestCase):

    def test_dest_path_deakin_bathymetry(self):
        good_nc = os.path.join(TEST_ROOT, 'Victorian-coast_Bathy_10m.tif')
        self.assertEqual(dest_path_deakin_bathymetry(good_nc), 'Deakin_University/bathymetry/Victorian-coast_Bathy_10m.tif')


if __name__ == '__main__':
    unittest.main()
