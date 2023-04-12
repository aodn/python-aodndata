import os
import unittest
from aodndata.aims.mmp_ctd import dest_path_aims_mmp_ctd


TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'AIMS_MMP-WQ_20061027T111208Z_WQN083_FV01_Profile-SBE19plus_C-20210831T061352Z.nc')

class TestMmpCtdHandler(unittest.TestCase):

    def test_good_path(self):
        self.assertEqual(dest_path_aims_mmp_ctd(GOOD_NC), os.path.join('AIMS/Marine_Monitoring_Program/CTD_profiles/2006',
                                                                          os.path.basename(GOOD_NC)))

if __name__ == '__main__':
    unittest.main()
