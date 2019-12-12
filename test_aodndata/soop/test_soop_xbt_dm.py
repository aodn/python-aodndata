import os
import unittest
from urllib.parse import urlparse

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType, FileType
from aodncore.testlib import HandlerTestCase
from aodncore.util import is_jpeg_file

from aodndata.soop.soop_xbt_dm import SoopXbtDmHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-XBT_T_20160106T110100Z_PX02_FV01_ID-150739.nc')


class TestSoopXbtDmHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopXbtDmHandler
        super(TestSoopXbtDmHandler, self).setUp()

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                   include_regexes=['IMOS_SOOP-XBT_T_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 2)
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f_nc.name, os.path.basename(GOOD_NC))
        self.assertEqual(f_nc.dest_path,
                         'IMOS/SOOP/SOOP-XBT/DELAYED/Line_PX02_Flores-Sea-Torres-Strait/2016/' + os.path.basename(
                             GOOD_NC)
                         )
        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

        f_jpg = handler.file_collection.filter_by_attribute_id('file_type', FileType.JPEG)[0]
        image_path = os.path.join(urlparse(self.config.pipeline_config['global']['upload_uri']).path, f_jpg.dest_path)

        self.assertTrue(is_jpeg_file(image_path))


if __name__ == '__main__':
    unittest.main()
