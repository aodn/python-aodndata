import unittest
import os

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodndata.srs.srs_altimetry import SrsAltHandler
from test_aodncore.testlib import HandlerTestCase

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE = os.path.join(TEST_ROOT,
                       'IMOS_SRSALT_TCPS_20150818T023000Z_BASJAS_FV01_SBE37d30m.nc')


class TestSrsAltHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsAltHandler
        super(TestSrsAltHandler, self).setUp()

    def test_netcdf(self):
        handler = self.run_handler(NC_FILE,
                                   include_regexes=['IMOS_SRSALT_TCPS_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']}
                                   )
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/ALTIMETRY/calibration_validation/SRSBASJAS/CTD_timeseries',
                                      os.path.basename(NC_FILE)))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
