import httpretty
import json
import os
import unittest

from aodncore.pipeline import PipelineFileCollection, PipelineFile, PipelineFilePublishType
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase

from aodndata.moorings.products_handler import MooringsProductsHandler

TEST_ROOT = os.path.dirname(__file__)
GOOD_MANIFEST = os.path.join(TEST_ROOT, 'test_product.json_manifest')

GETCAPABILITIES_FILE = os.path.join(TEST_ROOT, 'getCapabilities.xml')
GETFEATURE_FILE = os.path.join(TEST_ROOT, 'getFeature.json')

with open(GETCAPABILITIES_FILE) as f:
    TEST_GETCAPABILITIES_RESPONSE = httpretty.Response(f.read())

with open(GETFEATURE_FILE) as f:
    TEST_GETFEATURE_JSON = f.read()
TEST_GETFEATURE_RESPONSE = httpretty.Response(TEST_GETFEATURE_JSON)

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

    @httpretty.activate
    def test_good_manifest(self):
        httpretty.register_uri(httpretty.GET, self.config.pipeline_config['global']['wfs_url'],
                               responses=[TEST_GETCAPABILITIES_RESPONSE, TEST_GETCAPABILITIES_RESPONSE,
                                          TEST_GETFEATURE_RESPONSE]
                               )
        # TODO: remove double TEST_GETCAPABILITIES_RESPONSE above, when it's no longer needed

        upload_broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        upload_broker.upload(INPUT_FILE_COLLECTION)

        handler = self.run_handler(GOOD_MANIFEST)
        self.assertCountEqual(INPUT_FILE_COLLECTION.get_attribute_list('dest_path'),
                              handler.input_file_collection.get_attribute_list('dest_path')
                              )
        self.assertEqual(len(handler.file_collection), 3)
        self.assertEqual(len(handler.excluded_files), 1)


if __name__ == '__main__':
    unittest.main()
