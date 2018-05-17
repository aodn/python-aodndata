import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.testlib import HandlerTestCase
from aodndata.srs.srs_oc_ljco import SrsOcLjcoHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE_ACS = os.path.join(TEST_ROOT,
                           'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV01_ACS-hourly-wcc_C-20170101T000000Z.nc')

NC_FILE_DALEC = os.path.join(TEST_ROOT,
                             'IMOS_SRS-OC-LJCO_F_20170320T230011Z_LJCO_FV01_DALEC_20170321T001305Z.nc')

NC_FILE_BAD_NAME_1 = os.path.join(TEST_ROOT,
                                  'IMOS_SRS-OC-LJCO_F_20170320T230011Z_LJCO_FV01_TEST_20170321T001305Z.nc')

NC_FILE_BAD_NAME_2 = os.path.join(TEST_ROOT,
                                  'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV01_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc')

NC_FILE_BAD_NAME_3 = os.path.join(TEST_ROOT,
                                  'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV01_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc')

NC_FILE_BAD_NAME_4 = os.path.join(TEST_ROOT,
                                  'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV04_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc')

NC_FILE_BAD_NAME_5 = os.path.join(TEST_ROOT,
                                  'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_UNKONWN_FV04_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc')

NC_FILE_WQM_HOURLY = os.path.join(TEST_ROOT,
                                  'IMOS_SRS-OC-LJCO_KOSTUZ_20160630T231115Z_SRC_FV01_WQM-hourly.nc')

NC_FILE_OCR_DAILY = os.path.join(TEST_ROOT,
                                 'IMOS_SRS-OC-LJCO_EFZ_20160630T000000Z_SRC_FV02_HyperOCR-daily.nc')


class TestSrsOcLjcoHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsOcLjcoHandler
        super(TestSrsOcLjcoHandler, self).setUp()

    def test_netcdf_acs(self):
        handler = self.run_handler(NC_FILE_ACS,
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

    def test_netcdf_dalec(self):
        handler = self.run_handler(NC_FILE_DALEC)
        f = handler.file_collection[0]
        self.assertEqual(f.dest_path, os.path.join('IMOS/SRS/OC/LJCO/DALEC/2017/03/', os.path.basename(NC_FILE_DALEC)))

    def test_good_netcdf_path(self):
        self.assertEqual(SrsOcLjcoHandler.dest_path(NC_FILE_WQM_HOURLY),
                         os.path.join('IMOS/SRS/OC/LJCO/WQM-hourly/2016/06/30/',
                                      os.path.basename(NC_FILE_WQM_HOURLY)))

        self.assertEqual(SrsOcLjcoHandler.dest_path(NC_FILE_OCR_DAILY),
                         os.path.join('IMOS/SRS/OC/LJCO/HyperOCR-daily/2016/',
                                      os.path.basename(NC_FILE_OCR_DAILY)))

    def test_bad_products_netcdf(self):
        with self.assertRaises(InvalidFileNameError):
            SrsOcLjcoHandler.dest_path(NC_FILE_BAD_NAME_1)

        with self.assertRaises(InvalidFileNameError):
            SrsOcLjcoHandler.dest_path(NC_FILE_BAD_NAME_2)

        with self.assertRaises(InvalidFileNameError):
            SrsOcLjcoHandler.dest_path(NC_FILE_BAD_NAME_3)

        with self.assertRaises(InvalidFileNameError):
            SrsOcLjcoHandler.dest_path(NC_FILE_BAD_NAME_4)

        with self.assertRaises(InvalidFileNameError):
            SrsOcLjcoHandler.dest_path(NC_FILE_BAD_NAME_5)


if __name__ == '__main__':
    unittest.main()
