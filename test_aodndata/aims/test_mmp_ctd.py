import os
import unittest

from aodncore.pipeline import PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.aims.mmp_ctd import MmpCtdHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'AIMS_MMP-WQ_20061027T111208Z_WQN083_FV01_Profile-SBE19plus_C-20210831T061352Z.nc')

class TestMmpCtdHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = MmpCtdHandler
        super(TestMmpCtdHandler, self).setUp()


    def test_handler(self):
        handler = self.run_handler(GOOD_NC)
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

    def test_good_path(self):
        dest_path = MmpCtdHandler.dest_path(GOOD_NC)
        expected_path = os.path.join("AIMS/Marine_Monitoring_Program/CTD_profiles/2006", os.path.basename(GOOD_NC))
        self.assertEqual(expected_path, dest_path)


if __name__ == '__main__':
    unittest.main()
