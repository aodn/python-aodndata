import json
import os
import unittest
from unittest.mock import patch

from aodncore.pipeline import PipelineFileCollection, PipelineFile, PipelineFilePublishType
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase

from aodndata.moorings.products_handler import MooringsProductsHandler

TEST_ROOT = os.path.dirname(__file__)
GOOD_MANIFEST = os.path.join(TEST_ROOT, 'test_product.json_manifest')

GETFEATURE_FILE = os.path.join(TEST_ROOT, 'getFeature.json')
GETFEATURE_OLD_PRODUCTS_FILE = os.path.join(TEST_ROOT, 'getFeature_old_products.json')

with open(GETFEATURE_FILE) as f:
    TEST_GETFEATURE_JSON = f.read()

with open(GETFEATURE_OLD_PRODUCTS_FILE) as f:
    TEST_GETFEATURE_OLD_PRODUCTS_JSON = f.read()

features = json.loads(TEST_GETFEATURE_JSON)['features']
INPUT_FILE_COLLECTION = PipelineFileCollection()
for f in features:
    pf = PipelineFile(
        os.path.join(TEST_ROOT, os.path.basename(f['properties']['url'])),
        dest_path=f['properties']['url']
    )
    pf.publish_type = PipelineFilePublishType.UPLOAD_ONLY
    INPUT_FILE_COLLECTION.add(pf)


class TestMooringsProductsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = MooringsProductsHandler
        super(TestMooringsProductsHandler, self).setUp()

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_good_manifest(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.return_value = TEST_GETFEATURE_JSON

        upload_broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        upload_broker.upload(INPUT_FILE_COLLECTION)

        handler = self.run_handler(GOOD_MANIFEST)
        self.assertCountEqual(INPUT_FILE_COLLECTION.get_attribute_list('dest_path'),
                              handler.input_file_collection.get_attribute_list('dest_path')
                              )
        self.assertEqual(len(handler.file_collection), 5)

        published_files = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                         PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(len(published_files), 3)
        for f in published_files:
            self.assertTrue(f.is_harvested and f.is_stored)

        deleted_files = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                       PipelineFilePublishType.DELETE_UNHARVEST)
        self.assertEqual(len(deleted_files), 2)
        for f in deleted_files:
            self.assertTrue(f.is_harvested and f.is_stored)

        self.assertEqual(len(handler.excluded_files), 1)


if __name__ == '__main__':
    unittest.main()
