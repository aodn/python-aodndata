import os
import unittest
from shutil import copyfile

from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_xbt_nrt import SoopXbtNrtHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_CSV = os.path.join(TEST_ROOT, 'IMOS_SOOP-XBT_T_20150813T063800Z_5BPB3_002301_FV00.csv')


class TestSoopXbtNrtHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopXbtNrtHandler
        super(TestSoopXbtNrtHandler, self).setUp()

    def test_rsync_manifest_file(self):
        MANIFEST_FILE = os.path.join(self.temp_dir, 'soop_xbt_nrt.manifest')
        test_csv_path = os.path.join(self.temp_dir,
                                     'SOOP/SOOP_XBT_ASF_SST/data_sorted/XBT/sbddata/5BPB3_Patricia-Schulte/2015')
        os.makedirs(test_csv_path)
        copyfile(GOOD_CSV, os.path.join(test_csv_path, os.path.basename(GOOD_CSV)))

        with open(MANIFEST_FILE, 'w') as f:
            f.write(os.path.join(test_csv_path, os.path.basename(GOOD_CSV)))

        handler = self.run_handler(MANIFEST_FILE,
                                   include_regexes=['IMOS_SOOP-XBT_T.*\.csv']
                                   )
        f = handler.file_collection[0]
        self.assertEqual(f.dest_path, 'IMOS/SOOP/SOOP-XBT/REALTIME/5BPB3_Patricia-Schulte/2015/IMOS_SOOP-XBT_T_20150813T063800Z_5BPB3_002301_FV00.csv')



if __name__ == '__main__':
    unittest.main()
