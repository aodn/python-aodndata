from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

from aodndata.soop.soop_xbt_nrt import dest_path_soop_xbt_nrt
from aodncore.pipeline.exceptions import InvalidFileNameError


class TestSoopXbtNrtHandler(unittest.TestCase):

    def test_dest_path_soop_xbt_nrt(self):
        good_csv = '/mnt/ebs/wip/SOOP/XBT/sbddata/5BPB3_Patricia-Schulte/2015/IMOS_SOOP-XBT_T_20150813T063800Z_5BPB3_002301_FV00.csv'
        self.assertEqual(dest_path_soop_xbt_nrt(good_csv), 'IMOS/SOOP/SOOP-XBT/REALTIME/5BPB3_Patricia-Schulte/2015/IMOS_SOOP-XBT_T_20150813T063800Z_5BPB3_002301_FV00.csv')

        bad_csv = 'IMOS_SOOP-XBT_T_20150813T063800Z_5BPB3_002301_FV00.csv'
        with self.assertRaises(InvalidFileNameError):
            dest_path_soop_xbt_nrt(bad_csv)


if __name__ == '__main__':
    unittest.main()
