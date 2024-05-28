import os
import unittest

from aodndata.soop.soop_fishsoop import SoopFishSoopHandler
from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE_NRT = 'IMOS_SOOP-FishSOOP_TP_20240310T094642Z_FV00_786.nc'


class TestSoopFishSoop(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopFishSoopHandler
        super(TestSoopFishSoop, self).setUp()
        self.nc_file_nrt = os.path.join(TEST_ROOT, NC_FILE_NRT)

    def test_dest_path_soop_fishsoop(self):
        handler = self.run_handler(self.nc_file_nrt,
                                   check_params={'checks': ['cf:1.6', 'imos:1.4']}
                                   )

        f = handler.file_collection[0]

        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertEqual(f.dest_path,
                         os.path.join(f"IMOS/SOOP/SOOP-FishSOOP/REALTIME/2024/03/{os.path.basename(self.nc_file_nrt)}"))

        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
