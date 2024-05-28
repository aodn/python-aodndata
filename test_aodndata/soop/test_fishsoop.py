import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodndata.soop.soop_fishsoop import dest_path_soop_fishsoop

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSoopFishSoop(unittest.TestCase):

    def test_dest_path_soop_fishsoop(self):
        good_nc_nrt = os.path.join(TEST_ROOT, 'IMOS_SOOP-FishSOOP_PT_20240310T094642Z_FV00_786.nc')
        self.assertEqual(dest_path_soop_fishsoop(good_nc_nrt),
                         'IMOS/SOOP/SOOP-FishSOOP/REALTIME/2024/03/{basename}'.format(
                             basename=os.path.basename(good_nc_nrt)),
        )

        good_nc_dm = os.path.join(TEST_ROOT, 'IMOS_SOOP-FishSOOP_TP_20240310T094642Z_FV01_786.nc')
        self.assertEqual(dest_path_soop_fishsoop(good_nc_dm),
                         'IMOS/SOOP/SOOP-FishSOOP/DELAYED/2024/03/{basename}'.format(
                             basename=os.path.basename(good_nc_dm)),
        )


if __name__ == '__main__':
    unittest.main()
