import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType, FileType
from aodncore.pipeline.exceptions import MissingFileError
from aodncore.testlib import HandlerTestCase

from aodndata.argo.handler import ArgoHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
RSYNC_MANIFEST_FILE = os.path.join(TEST_ROOT, 'test_argo_add.rsync_manifest')
MISSING_FILE_RSYNC_MANIFEST_FILE = os.path.join(TEST_ROOT, 'test_argo_add_missing_file.rsync_manifest')
NON_NC_RSYNC_MANIFEST_FILE = os.path.join(TEST_ROOT, 'test_argo_add_non_nc.rsync_manifest')


class TestArgoHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = ArgoHandler
        super(TestArgoHandler, self).setUp()

    def test_rsync_manifest_file(self):
        handler = self.handler_class(RSYNC_MANIFEST_FILE)
        handler.resolve_params = {'relative_path_root': os.path.join(TEST_ROOT, 'Argo/dac')}
        handler.run()

        file_added = handler.file_collection[0]
        file_deleted = handler.file_collection[1]

        """ argo handler is forcing the relative_path_root. we need to make sure the handler
            is not throwing any error """
        self.assertIsNone(handler.error)
        self.assertEqual(file_added.check_type, PipelineFileCheckType.FORMAT_CHECK)
        self.assertEqual(file_added.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(file_added.dest_path, 'IMOS/Argo/dac/csiro/1901119/profiles/D1901119_001.nc')
        self.assertTrue(file_added.is_stored)

        self.assertEqual(file_deleted.publish_type, PipelineFilePublishType.DELETE_UNHARVEST)
        self.assertEqual(file_deleted.dest_path, 'IMOS/Argo/dac/handlers/dummy/aoml/1900728/1900728_Rtraj.nc')

    def test_missing_file_rsync_manifest_file(self):
        # check file in manifest but not in filesystem
        handler = self.handler_class(MISSING_FILE_RSYNC_MANIFEST_FILE)
        handler.resolve_params = {'relative_path_root': os.path.join(TEST_ROOT, 'Argo/dac')}
        handler.run()

        self.assertIsInstance(handler.error, MissingFileError)

    def test_non_nc_rsync_manifest_file(self):
        # check file not finishing with nc extension is not pusblished
        handler = self.handler_class(NON_NC_RSYNC_MANIFEST_FILE)
        handler.resolve_params = {'relative_path_root': os.path.join(TEST_ROOT, 'Argo/dac')}
        handler.run()
        bad_file = handler.file_collection.filter_by_attribute_value('name', 'D1901119_001.bad')[0]
        good_file_deletion = handler.file_collection.filter_by_attribute_value('file_type', FileType.NETCDF)[0]

        self.assertEqual(bad_file.publish_type, PipelineFilePublishType.NO_ACTION)
        self.assertEqual(good_file_deletion.publish_type, PipelineFilePublishType.DELETE_UNHARVEST)


if __name__ == '__main__':
    unittest.main()
