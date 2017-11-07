import os
import unittest

from aodndata.argo.handler import ArgoHandler
from test_aodncore.testlib import HandlerTestCase

TEST_ROOT = os.path.join(os.path.dirname(__file__))
RSYNC_MANIFEST_FILE = os.path.join(TEST_ROOT, 'test_argo_add.rsync_manifest')


class TestArgoHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = ArgoHandler
        super(TestArgoHandler, self).setUp()

    def test_rsync_manifest_file(self):
        handler = self.handler_class(RSYNC_MANIFEST_FILE)
        handler.relative_path_root = TEST_ROOT
        handler.run()


if __name__ == '__main__':
    unittest.main()
