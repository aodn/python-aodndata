import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase

from aodndata.srs.srs_oc_bodbaw import SrsOcBodBawHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE_CRUISE_STATION = os.path.join(TEST_ROOT,
                                      'IMOS_SRS-OC-BODBAW_X_20060308T022541Z_SWAIN-GBR080306_4-absorption-total-AC9_FV02_END-20060308T022541Z.nc')
NC_FILE = os.path.join(TEST_ROOT,
                       'IMOS_SRS-OC-BODBAW_X_20091109T000500Z_SB2009_11-absorption-CDOM_FV02_END-20100722T042400Z_C-20180522T160601Z.nc')
CSV_FILE = os.path.join(TEST_ROOT,
                        'IMOS_SRS-OC-BODBAW_X_20010102T072900Z_au0106-pigment_FV02_END-20010308T033800Z_C-20170101T000000Z.csv')
PNG_FILE = os.path.join(TEST_ROOT,
                        'IMOS_SRS-OC-BODBAW_X_20010102T072900Z_au0106-pigment_FV02_END-20010308T033800Z_C-20170101T000000Z.png')


class TestSrsOcBodBawHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsOcBodBawHandler
        super(TestSrsOcBodBawHandler, self).setUp()

    def test_netcdf(self):
        handler = self.run_handler(NC_FILE,
                                   include_regexes=[r'IMOS_SRS-OC-BODBAW_X_.*\.nc'],
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'}
                                   )

        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/OC/BODBAW/SB2009_11/absorption/',
                                      'IMOS_SRS-OC-BODBAW_X_20091109T000500Z_SB2009_11-absorption-CDOM_FV02_END-20100722T042400Z.nc'))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_netcdf_station_id(self):
        """
        test NetCDF handling. Check only the cruise_id(and not the station_id) appears in the folder structure
        :return:
        """
        handler = self.run_handler(NC_FILE_CRUISE_STATION,
                                   include_regexes=[r'IMOS_SRS-OC-BODBAW_X_.*\.nc'],
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'}
                                   )

        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/OC/BODBAW/SWAIN/absorption/'
                                      'IMOS_SRS-OC-BODBAW_X_20060308T022541Z_SWAIN-GBR080306_4-absorption-total-AC9_FV02_END-20060308T022541Z.nc'))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_csv(self):
        handler = self.run_handler(CSV_FILE)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        dest_path = f.dest_path
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/OC/BODBAW/au0106/pigment/',
                                      'IMOS_SRS-OC-BODBAW_X_20010102T072900Z_au0106-pigment_FV02_END-20010308T033800Z.csv'))
        self.assertTrue(f.is_stored)

    def test_png(self):
        handler = self.run_handler(PNG_FILE)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        dest_path = f.dest_path
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/OC/BODBAW/au0106/pigment/',
                                      'IMOS_SRS-OC-BODBAW_X_20010102T072900Z_au0106-pigment_FV02_END-20010308T033800Z.png'))
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
