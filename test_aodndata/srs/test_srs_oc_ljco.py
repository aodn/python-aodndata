import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase

from aodndata.srs.srs_oc_ljco import SrsOcLjcoHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE = os.path.join(TEST_ROOT,
                       'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV01_ACS-hourly-wcc_C-20170101T000000Z.nc')


class TestSrsOcLjcoHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsOcLjcoHandler
        super(TestSrsOcLjcoHandler, self).setUp()

    def test_netcdf(self):
        handler = self.run_handler(NC_FILE,
                                   include_regexes=['IMOS_SRS-OC-LJCO_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']}
                                   )
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/OC/LJCO/ACS-hourly/2016/06/01/',
                                      'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV01_ACS-hourly-wcc.nc'))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
