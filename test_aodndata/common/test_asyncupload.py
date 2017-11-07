import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileFormatError
from aodndata.common.asyncupload import AsyncUploadHandler
from test_aodncore.testlib import HandlerTestCase

TEST_ROOT = os.path.join(os.path.dirname(__file__))
MAP_MANIFEST_FILE = os.path.join(TEST_ROOT, 'test.map_manifest')
NOT_MAP_MANIFEST_FILE = os.path.join(TEST_ROOT, 'invalid.png')


class TestAsyncUploadHandlerHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AsyncUploadHandler
        super(TestAsyncUploadHandlerHandler, self).setUp()

    def test_map_manifest_file(self):
        handler = self.run_handler(MAP_MANIFEST_FILE, resolve_params={'relative_path_root': TEST_ROOT})

        expected_dest_path = 'UNITTEST/NOT/A/REAL/PATH'
        self.assertEqual(expected_dest_path, handler.file_collection[0].dest_path)

    def test_not_map_manifest_file(self):
        self.run_handler_with_exception(InvalidFileFormatError, NOT_MAP_MANIFEST_FILE)


if __name__ == '__main__':
    unittest.main()
