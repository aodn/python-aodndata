import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase

from aodndata.srs.srs_altimetry import SrsAltHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE_SBE26 = os.path.join(TEST_ROOT,
                       'IMOS_SRSALT_PT_20160919T020500Z_BASS3A_FV01_SBE26d49m.nc')
NC_FILE_ST_CM = os.path.join(TEST_ROOT,
                             'IMOS_SRSALT_UVT_20011218T000000Z_BASJAS_FV01_ST_CMd19m.nc')


class TestSrsAltHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsAltHandler
        super(TestSrsAltHandler, self).setUp()

    def test_netcdf_publish(self):
        handler = self.run_handler(NC_FILE_SBE26,
                                   include_regexes=[r'IMOS_SRSALT_PT_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']}
                                   )

        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/ALTIMETRY/calibration_validation/SRSBASS3A/Pressure_gauge',
                                      os.path.basename(NC_FILE_SBE26)))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_destpath(self):
        dest_path = SrsAltHandler.dest_path(NC_FILE_ST_CM)
        self.assertEqual(dest_path,
                 os.path.join('IMOS/SRS/ALTIMETRY/calibration_validation/SRSBASJAS/Velocity',
                              os.path.basename(NC_FILE_ST_CM)))


if __name__ == '__main__':
    unittest.main()
