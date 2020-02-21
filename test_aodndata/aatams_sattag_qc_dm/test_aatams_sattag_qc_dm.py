import os
import unittest

from aodncore.pipeline import PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.aatams_sattag_qc_dm.aatams_sattag_qc_dm import AatamsSattagQcDmHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_ZIP = os.path.join(TEST_ROOT, 'simple_zip.zip')
AATAMS_SATTAG_DM_BASE = "IMOS/AATAMS/AATAMS_SATTAG_QC_DM"


class TestAatamsDmHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AatamsSattagQcDmHandler
        super(TestAatamsDmHandler, self).setUp()

    def test_harvest_csvs_in_zip(self):
        handler = self.run_handler(GOOD_ZIP)
        for file in handler.file_collection:
            self.assertEqual(file.publish_type,
                             PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertEqual(AATAMS_SATTAG_DM_BASE,
                             os.path.dirname(file.dest_path))


if __name__ == '__main__':
    unittest.main()
