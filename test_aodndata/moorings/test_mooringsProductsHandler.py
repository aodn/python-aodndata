import os
import re
import unittest

from aodncore.pipeline import PipelineFilePublishType, PipelineFileCheckType, FileType
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodncore.testlib import HandlerTestCase, make_zip
from aodndata.moorings.products_handler import MooringsProductsHandler

TEST_ROOT = os.path.dirname(__file__)
GOOD_MANIFEST = os.path.join(TEST_ROOT, 'product_manifest.json')


class TestMooringsProductsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = MooringsProductsHandler
        super(TestMooringsProductsHandler, self).setUp()

    def test_good_manifest(self):
        self.run_handler(GOOD_MANIFEST)


if __name__ == '__main__':
    unittest.main()
