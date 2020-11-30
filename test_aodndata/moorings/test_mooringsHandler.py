import os
import re
import unittest

from aodncore.pipeline import PipelineFilePublishType, PipelineFileCheckType, FileType
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodncore.testlib import HandlerTestCase, make_zip
from aodndata.moorings.handlers import MooringsHandler

TEST_ROOT = os.path.dirname(__file__)
BAD_NC = os.path.join(TEST_ROOT,
                      'IMOS_ANMN-NRS_CDEKOSTUZ_20140703T021045Z_NRSMAI_FV00_Profile-BAD_C-20160524T003914Z.nc')
GOOD_NC_BASENAME = 'IMOS_ANMN-NRS_CDEKOSTUZ_20140703T021045Z_NRSMAI_FV01_Profile-SBE-19plus_C-20160524T003914Z.nc'
GOOD_NC = os.path.join(TEST_ROOT, GOOD_NC_BASENAME)
GOOD_PDF_BASENAME = 'IMOS_ANMN-NRS_20140703_NRSMAI_FV01_LOGSHT.pdf'
GOOD_PDF = os.path.join(TEST_ROOT, GOOD_PDF_BASENAME)
GOOD_PNG_BASENAME = 'IMOS_ANMN-NRS_NRSMAI_FV01_20140703T021045Z_LINE_C-20160524T003914Z.png'
GOOD_PNG = os.path.join(TEST_ROOT, GOOD_PNG_BASENAME)
GOOD_CNV_BASENAME = 'IMOS_ANMN-NRS_CTP_20140703_NRSMAI_FV00_CTDPRO.cnv'
GOOD_CNV = os.path.join(TEST_ROOT, GOOD_CNV_BASENAME)
BURST_NC_BASENAME = 'IMOS_ANMN-NRS_BCKOSTUZ_20081120T081531Z_NRSROT_FV01_NRSROT-0811-WQM-21_END-20081120T171535Z_C-20190418T000000Z.nc'
BURST_NC = os.path.join(TEST_ROOT, BURST_NC_BASENAME)
BURST_ADCP_BASENAME = 'IMOS_ANMN-WA_AETVZ_20181203T080004Z_WACA20_FV01_WACA20-1812-Signature250-194_END-20181204T090004Z_C-20190625T000000Z.nc'
BURST_ADCP = os.path.join(TEST_ROOT, BURST_ADCP_BASENAME)


class TestMooringsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = MooringsHandler
        super(TestMooringsHandler, self).setUp()

    def test_bad_name_file(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_NC, include_regexes=[r'IMOS_DWM-DA_.*\.nc'])

    # NetCDF tests

    def test_noncompliant_netcdf(self):
        self.run_handler_with_exception(ComplianceCheckFailedError, BAD_NC,
                                        include_regexes=[r'IMOS_ANMN-NRS_.*\.nc'],
                                        check_params={'checks': ['cf', 'imos:1.4']}
                                        )

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                   include_regexes=[r'IMOS_ANMN-NRS_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, GOOD_NC_BASENAME)
        self.assertEqual(f.dest_path, os.path.join('IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/', GOOD_NC_BASENAME))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)
        self.assertTrue(f.is_harvested)
        cleanup_regexes = [
            "{base}{wildcard}".format(
                base=re.escape("IMOS_ANMN-NRS_CDEKOSTUZ_20140703T021045Z_NRSMAI_FV01_Profile-SBE-19plus_C-"),
                wildcard=r".*\.[0-9a-f\-]{36}"
            )
        ]
        self.assertEqual(cleanup_regexes, handler.error_cleanup_regexes)

    def test_missing_attribute_for_dest_path(self):
        self.run_handler_with_exception(InvalidFileContentError, BAD_NC, include_regexes=[r'IMOS_ANMN-NRS_.*\.nc'])

    # TODO: def test_create_product(self):

    # TODO: def test_previous_versions(self):

    # PDF file tests

    def test_good_pdf(self):
        handler = self.run_handler(GOOD_PDF, include_regexes=[r'IMOS_ANMN-NRS_[0-9]{8}_.*\_LOGSHT.pdf'])
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.name, GOOD_PDF_BASENAME)
        self.assertEqual(f.dest_path, os.path.join('IMOS/ANMN/NRS/NRSMAI/Field_logsheets/', GOOD_PDF_BASENAME))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)
        self.assertTrue(f.is_harvested)
        cleanup_regexes = [
            "{base}{wildcard}".format(base=re.escape(GOOD_PDF_BASENAME), wildcard=r".*\.[0-9a-f\-]{36}")
        ]
        self.assertEqual(cleanup_regexes, handler.error_cleanup_regexes)

    # TODO: def test_bad_format_pdf(self):

    # PNG file tests

    def test_good_png(self):
        handler = self.run_handler(GOOD_PNG, include_regexes=[r'.*\.png'])
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.name, GOOD_PNG_BASENAME)
        self.assertEqual(f.dest_path, os.path.join('IMOS/ANMN/NRS/NRSMAI/plots/', GOOD_PNG_BASENAME))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)
        self.assertTrue(f.is_harvested)

    # TODO: def test_bad_format_png(self):

    # CNV file tests

    def test_good_cnv(self):
        handler = self.run_handler(GOOD_CNV, include_regexes=[r'.*\.cnv'])
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.name, GOOD_CNV_BASENAME)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/non-QC/cnv/', GOOD_CNV_BASENAME)
                         )
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)
        self.assertTrue(f.is_harvested)

    # TODO: def test_bad_cnv(self):

    def test_good_nc_zip(self):
        zip_file = make_zip(self.temp_dir, [GOOD_NC])
        handler = self.run_handler(zip_file,
                                   include_regexes=[r'IMOS_ANMN-NRS_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, GOOD_NC_BASENAME)
        self.assertEqual(f.dest_path, os.path.join('IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/', GOOD_NC_BASENAME))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)
        self.assertTrue(f.is_harvested)

    def test_good_and_bad_nc_zip(self):
        zip_file = make_zip(self.temp_dir, [GOOD_NC, BAD_NC])
        handler = self.run_handler_with_exception(ComplianceCheckFailedError, zip_file,
                                                  include_regexes=[r'IMOS_ANMN-NRS_.*\.nc'],
                                                  check_params={'checks': ['cf', 'imos:1.4']}
                                                  )
        self.assertEqual(len(handler.file_collection), 2)

        coll_dict = {f.name: f for f in handler.file_collection}
        f_good = coll_dict[GOOD_NC_BASENAME]
        self.assertTrue(f_good.is_checked)
        self.assertTrue(f_good.check_result.compliant)
        f_bad = coll_dict[os.path.basename(BAD_NC)]
        self.assertTrue(f_bad.is_checked)
        self.assertFalse(f_bad.check_result.compliant)

        # TODO: continue processing all files in zip, ignoring non-compliant ones
        # self.assertEqual(f_good.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        # self.assertEqual(f_bad.publish_type, PipelineFilePublishType.NO_ACTION)

    def test_all_formats_zip(self):
        zip_file = make_zip(self.temp_dir, [GOOD_NC, GOOD_PDF, GOOD_PNG, GOOD_CNV])
        handler = self.run_handler(zip_file,
                                   include_regexes=[r'IMOS_ANMN-NRS_.*\.(nc|pdf|png|cnv)'],
                                   check_params={'checks': ['cf', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 4)
        for f in handler.file_collection:
            self.assertTrue(f.is_checked)
            self.assertTrue(f.is_stored)
            self.assertTrue(f.is_harvested)

    def test_burst_processing(self):
        zip_file = make_zip(self.temp_dir, [BURST_NC, BURST_ADCP])
        handler = self.run_handler(zip_file,
                                   include_regexes=[r'.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.4'],
                                                 'skip_checks': ['check_dimension_order']}
                                   )

        self.assertEqual(3, len(handler.file_collection))

        f = handler.file_collection[0]
        self.assertEqual(f.name, BURST_NC_BASENAME)
        self.assertEqual(f.dest_path, os.path.join('IMOS/ANMN/NRS/NRSROT/Biogeochem_timeseries', BURST_NC_BASENAME))

        # there should also be a burst-averaged file
        f = handler.file_collection[-1]
        self.assertRegex(f.name, r'.*FV02_NRSROT-0811-WQM-21-burst-averaged.*')
        self.assertRegex(f.dest_path, r'IMOS/ANMN/NRS/NRSROT/Biogeochem_timeseries/burst-averaged/')

        for f in handler.file_collection:
            self.assertTrue(f.is_checked)
            self.assertTrue(f.is_stored)
            self.assertTrue(f.is_harvested)


if __name__ == '__main__':
    unittest.main()
