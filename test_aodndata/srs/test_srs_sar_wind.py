import os
import unittest
from urllib.parse import urlparse

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType, FileType
from aodncore.testlib import HandlerTestCase
from aodncore.util import is_png_file

from aodndata.srs.srs_surface_waves import SrsSarWindHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SRS-Surface-Waves_M_20200405_Coastal-Wind-Sentinel-1B_FV01_DM00-021005-027D80-33D5.nc')


class TestSrsSarWindHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsSarWindHandler
        super(TestSrsSarWindHandler, self).setUp()

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                   include_regexes=[r'IMOS_SRS-Surface-Waves_M_.*Coastal-Wind.*\.nc'],
                                   #check_params={'checks': ['cf:1.6', 'imos:1.4']},
                                   check_params={'checks': ['imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 2)
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f_nc.name, os.path.basename(GOOD_NC))
        self.assertEqual(os.path.join('IMOS/SRS/Surface-Waves/SAR_Wind/DELAYED/SENTINEL-1B/2020/04/05',
                                      os.path.basename(GOOD_NC)),
                         f_nc.dest_path)
        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

        f_png = handler.file_collection.filter_by_attribute_id('file_type', FileType.PNG)[0]
        image_path = os.path.join(urlparse(self.config.pipeline_config['global']['upload_uri']).path, f_png.dest_path)

        self.assertTrue(is_png_file(image_path))


if __name__ == '__main__':
    unittest.main(verbosity=2)
