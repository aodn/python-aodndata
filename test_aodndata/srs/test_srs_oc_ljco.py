import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.testlib import HandlerTestCase
from aodndata.srs.srs_oc_ljco import SrsOcLjcoHandler


TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE_ACS = os.path.join(TEST_ROOT,
                           'IMOS_SRS-OC-LJCO_FTZ_20211201T005626Z_LJCO_FV01_ACS-hourly-wcc_END-20211201T011614Z.nc')

NC_FILE_BAD_NAME = {'IMOS_SRS-OC-LJCO_F_20170320T230011Z_LJCO_FV01_TEST_20170321T001305Z.nc',
                    'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV01_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc',
                    'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_SRC_FV04_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc',
                    'IMOS_SRS-OC-LJCO_FTZ_20160601T004207Z_UNKONWN_FV04_BADINSTRUMENTNAME-BADTIMECOV-wcc_C-20170101T000000Z.nc'}

SRS_S3_PREFIX = 'IMOS/SRS/OC/LJCO/'
NC_VARIOUS_PATH = {'IMOS_SRS-OC-LJCO_BFZ_20211201T042615Z_LJCO_FV01_EcoTriplet-hourly_END-20211201T052514Z.nc': 'EcoTriplet-hourly/2021/12/01',
                   'IMOS_SRS-OC-LJCO_BFZ_20211202T002459Z_LJCO_FV01_EcoTriplet-daily_END-20211203T002459Z.nc': 'EcoTriplet-daily/2021/',
                   'IMOS_SRS-OC-LJCO_EF_20211217T232615Z_LJCO_FV01_HyperOCR-hourly_END-20211218T002614Z.nc': 'HyperOCR-hourly/2021/12/17/',
                   'IMOS_SRS-OC-LJCO_EF_20211217T232615Z_LJCO_FV02_HyperOCR-hourly_END-20211218T002614Z.nc': 'HyperOCR-hourly/2021/12/17/fv02-products',
                   'IMOS_SRS-OC-LJCO_EF_20211218T013000Z_LJCO_FV02_HyperOCR-daily_END-20211219T001500Z.nc': 'HyperOCR-daily/2021/fv02-products',
                   'IMOS_SRS-OC-LJCO_KOSTUZ_20211201T042500Z_LJCO_FV01_WQM-daily_END-20211202T002500Z.nc': 'WQM-daily/2021/',
                   'IMOS_SRS-OC-LJCO_BFZ_20211201T042615Z_LJCO_FV01_EcoTriplet-hourly_END-20211201T052514Z.nc': 'EcoTriplet-hourly/2021/12/01',
                   'IMOS_SRS-OC-LJCO_FTZ_20211201T122626Z_LJCO_FV01_ACS-hourly-wcc_END-20211201T131517Z.nc': 'ACS-hourly/2021/12/01/',
                   'IMOS_SRS-OC-LJCO_FTZ_20211201T122626Z_LJCO_FV01_ACS-daily-wcc_END-20211201T131517Z.nc': 'ACS-daily/2021/',
                   'IMOS_SRS-OC-LJCO_FZ_20211203T082615Z_LJCO_FV01_BB9-hourly_END-20211203T092614Z.nc': 'BB9-hourly/2021/12/03/',
                   'IMOS_SRS-OC-LJCO_FZ_20211204T002459Z_LJCO_FV01_BB9-daily_END-20211205T002459Z.nc': 'BB9-daily/2021',
                   'IMOS_SRS-OC-LJCO_F_20160526T231430Z_LJCO_FV01_DALEC_END-20160527T045958Z.nc': 'DALEC/2016/05',
                   'IMOS_SRS-OC-LJCO_F_20160526T231553Z_LJCO_FV02_DALEC_END-20160527T025949Z.nc': 'DALEC/2016/05/fv02-products'
                   }


class TestSrsOcLjcoHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsOcLjcoHandler
        super(TestSrsOcLjcoHandler, self).setUp()

    def test_various_path(self):
        for nc_file in NC_VARIOUS_PATH.keys():
            dest_path = SrsOcLjcoHandler.dest_path(os.path.join(TEST_ROOT, nc_file))
            expected_path = os.path.join(SRS_S3_PREFIX, NC_VARIOUS_PATH[nc_file], nc_file)
            self.assertEqual(dest_path, expected_path)

    def test_handler(self):
        handler = self.run_handler(NC_FILE_ACS,
                                   include_regexes=[r'IMOS_SRS-OC-LJCO_.*\.nc'],
                                   check_params={'checks': ['cf:1.6', 'imos:1.4']}
                                   )

        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/OC/LJCO/ACS-hourly/2021/12/01/',
                                      'IMOS_SRS-OC-LJCO_FTZ_20211201T005626Z_LJCO_FV01_ACS-hourly-wcc_END-20211201T011614Z.nc'))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


    def test_bad_products_netcdf(self):
        with self.assertRaises(InvalidFileNameError):
            for nc_file in NC_FILE_BAD_NAME:
                SrsOcLjcoHandler.dest_path(nc_file)


if __name__ == '__main__':
    unittest.main()
