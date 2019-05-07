import os
import unittest

from aodndata.curtin.soop_rad_aodn import dest_path_soop_rad_aodn

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'IMOS_SRS-OC_DALEC-R_20141009T050350Z_SOOP_FV02_REFLECTANCE_20141009T050350Z.nc')


class TestSoopRadAodnHandler(unittest.TestCase):

    def test_dest_path(self):
        self.assertEqual(dest_path_soop_rad_aodn(GOOD_NC), os.path.join('Curtin_University/Radiometer_DALEC/Unknown_Vessels',
                                                                          '2014',
                                                                          os.path.basename(GOOD_NC)))


if __name__ == '__main__':
    unittest.main()
