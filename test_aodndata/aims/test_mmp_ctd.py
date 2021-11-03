import os
import unittest

from aodndata.aims.mmp_ctd import dest_path_mmp_ctd

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestMmpCtd(unittest.TestCase):

    def test_dest_path_mmp_ctd(self):
        good_nc = os.path.join(TEST_ROOT, 'AIMS_MMP-WQ_20061027T111208Z_WQN083_FV01_Profile-SBE19plus_C-20210831T061352Z.nc')
        self.assertEqual('AIMS/Marine_Monitoring_Program/BUR4/Biogeochem_profiles/2006/AIMS_MMP-WQ_20061027T111208Z_WQN083_FV01_Profile-SBE19plus_C-20210831T061352Z.nc',
                         dest_path_mmp_ctd(good_nc))


if __name__ == '__main__':
    unittest.main()
