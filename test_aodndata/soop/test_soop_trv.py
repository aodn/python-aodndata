import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_trv import SoopTrvHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-TRV_B_20100225T073727Z_VMQ9273_FV01_END-20100225T131607Z_C-2016225T100000Z.nc')


class TestSoopTrvHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopTrvHandler
        super(TestSoopTrvHandler, self).setUp()

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                     include_regexes=['IMOS_SOOP-TRV_B_.*\.nc'],
                                     check_params={'checks': ['cf', 'imos:1.3']}
                                     )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20100225T073727Z_END-20100225T131607Z/chlorophyll/IMOS_SOOP-TRV_B_20100225T073727Z_VMQ9273_FV01_END-20100225T131607Z.nc')
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
