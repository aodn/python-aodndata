import os

from aodncore.pipeline import PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodncore.util.fileops import extract_zip

from aodndata.aatams.aatams_dm import AatamsDmHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_ZIP = os.path.join(TEST_ROOT, 'kp01.zip')
AATAMS_SATTAG_DM_BASE = "IMOS/AATAMS/AATAMS_SATTAG_DM"


class TestAatamsDmHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AatamsDmHandler
        super(TestAatamsDmHandler, self).setUp()

    def test_push_zip_file(self):
        """
        pushing zip file containing mdb to incoming. ZIP is archived. MDB is only harvested, not uploaded
        """
        handler = self.run_handler(GOOD_ZIP)

        f_mdb = handler.file_collection.filter_by_attribute_value('extension', '.mdb')[0]
        self.assertEqual(f_mdb.publish_type, PipelineFilePublishType.HARVEST_ONLY)

        f_zip = handler.file_collection.filter_by_attribute_value('extension', '.zip')[0]
        self.assertEqual(f_zip.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join(AATAMS_SATTAG_DM_BASE, os.path.basename(GOOD_ZIP)),
                         f_zip.archive_path)

    def test_push_mdb_file(self):
        """
        unzipping ZIP manually prior to running handler to simulate pipeline on mdb pushed to incoming
        """
        test_incoming_path = os.path.join(self._temp_dir, 'AATAMS')
        os.makedirs(test_incoming_path)

        # Extract all the contents of zip file in different directory
        extract_zip(GOOD_ZIP, test_incoming_path)
        mdb_path = os.path.join(test_incoming_path, os.path.basename(GOOD_ZIP).replace('.zip', '.mdb'))

        handler = self.run_handler(mdb_path)
        f_mdb = handler.file_collection.filter_by_attribute_value('extension', '.mdb')[0]
        self.assertEqual(f_mdb.publish_type, PipelineFilePublishType.HARVEST_ONLY)

    def test_lftp_manifest_file(self):
        manifest_file = os.path.join(self._temp_dir, 'aatams_dm.manifest')

        with open(manifest_file, 'w') as f:
            f.write(GOOD_ZIP)

        handler = self.run_handler(manifest_file)

        f_mdb = handler.file_collection.filter_by_attribute_value('extension', '.mdb')[0]
        self.assertEqual(f_mdb.publish_type, PipelineFilePublishType.HARVEST_ONLY)

        f_zip = handler.file_collection.filter_by_attribute_value('extension', '.zip')[0]
        self.assertEqual(f_zip.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
