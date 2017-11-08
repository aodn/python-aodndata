import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_xbt_dm import SoopXbtDmHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-XBT_T_20160106T110100Z_PX02_FV01_ID-150739.nc')
GOOD_JPG = os.path.join(TEST_ROOT, 'IMOS_SOOP-XBT_T_20160106T110100Z_PX02_FV01_ID-150739.jpg')


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
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-XBT/DELAYED/Line_PX02_Flores-Sea-Torres-Strait/2016/' + os.path.basename(
                             GOOD_NC)
                         )
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
