import os
import unittest

from aodncore.pipeline import PipelineFilePublishType, PipelineFileCheckType
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodndata.moorings.handlers import MooringsHandler
from test_aodncore.testlib import HandlerTestCase, make_zip

TEST_ROOT = os.path.join(os.path.dirname(__file__))
BAD_NC = os.path.join(TEST_ROOT,
                      'IMOS_ANMN-NRS_CDEKOSTUZ_20140703T021045Z_NRSMAI_FV00_Profile-BAD_C-20160524T003914Z.nc')
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_ANMN-NRS_CDEKOSTUZ_20140703T021045Z_NRSMAI_FV01_Profile-SBE-19plus_C-20160524T003914Z.nc')
GOOD_PDF = os.path.join(TEST_ROOT, 'IMOS_ANMN-NRS_20140703_NRSMAI_FV01_LOGSHT.pdf')
GOOD_PNG = os.path.join(TEST_ROOT, 'IMOS_ANMN-NRS_NRSMAI_FV01_20140703T021045Z_LINE_C-20160524T003914Z.png')
GOOD_CNV = os.path.join(TEST_ROOT, 'IMOS_ANMN-NRS_CTP_20140703_NRSMAI_FV00_CTDPRO.cnv')


class TestMooringsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = MooringsHandler
        super(TestMooringsHandler, self).setUp()

    def test_bad_name_file(self):
        handler = self.handler_class(BAD_NC,
                                     include_regexes=['IMOS_ABOS-DA_.*\.nc']
                                     )
        handler.run()

        self.assertIsInstance(handler.error, InvalidFileNameError)

    # NetCDF tests

    def test_noncompliant_netcdf(self):
        handler = self.handler_class(BAD_NC,
                                     include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                     check_params={'checks': ['cf', 'imos:1.4']}
                                     )
        handler.run()

        self.assertIsInstance(handler.error, ComplianceCheckFailedError)

    def test_good_netcdf(self):
        handler = self.handler_class(GOOD_NC,
                                     include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                     check_params={'checks': ['cf', 'imos:1.4']}
                                     )
        handler.run()
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
            self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertEqual(f.name, os.path.basename(GOOD_NC))
            self.assertEqual(f.dest_path,
                             'IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/' + os.path.basename(GOOD_NC)
                             )
            self.assertTrue(f.is_checked)
            self.assertTrue(f.is_stored)
            # TODO: self.assertTrue(f.is_harvested)

    def test_missing_attribute_for_dest_path(self):
        handler = self.handler_class(BAD_NC,
                                     include_regexes=['IMOS_ANMN-NRS_.*\.nc']
                                     )
        handler.run()

        self.assertIsInstance(handler.error, InvalidFileContentError)

    # TODO: def test_create_product(self):

    # TODO: def test_previous_versions(self):

    # PDF file tests

    def test_good_pdf(self):
        handler = self.handler_class(GOOD_PDF,
                                     include_regexes=['IMOS_ANMN-NRS_[0-9]{8}_.*\_LOGSHT.pdf']
                                     )
        handler.run()
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
            self.assertEqual(f.name, os.path.basename(GOOD_PDF))
            self.assertEqual(f.dest_path,
                             'IMOS/ANMN/NRS/NRSMAI/Field_logsheets/' + os.path.basename(GOOD_PDF)
                             )
            self.assertTrue(f.is_stored)

    # TODO: def test_bad_format_pdf(self):

    # PNG file tests

    def test_good_png(self):
        handler = self.handler_class(GOOD_PNG, include_regexes=['.*\.png'])
        handler.run()
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
            self.assertEqual(f.name, os.path.basename(GOOD_PNG))
            self.assertEqual(f.dest_path, 'IMOS/ANMN/NRS/NRSMAI/plots/' + os.path.basename(GOOD_PNG))
            self.assertTrue(f.is_stored)

    # TODO: def test_bad_format_png(self):

    # CNV file tests

    def test_good_cnv(self):
        handler = self.handler_class(GOOD_CNV, include_regexes=['.*\.cnv'])
        handler.run()
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
            self.assertEqual(f.name, os.path.basename(GOOD_CNV))
            self.assertEqual(f.dest_path,
                             'IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/non-QC/cnv/' + os.path.basename(GOOD_CNV)
                             )
            self.assertTrue(f.is_stored)

    # TODO: def test_bad_cnv(self):

    # TODO: ZIP file tests
    def test_good_nc_zip(self):
        zip_file = make_zip(self.temp_dir, [GOOD_NC])
        handler = self.handler_class(zip_file,
                                     include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                     check_params={'checks': ['cf', 'imos:1.4']}
                                     )
        handler.run()
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
            self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertEqual(f.name, os.path.basename(GOOD_NC))
            self.assertEqual(f.dest_path,
                             'IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/' + os.path.basename(GOOD_NC)
                             )
            self.assertTrue(f.is_checked)
            self.assertTrue(f.is_stored)
            # TODO: self.assertTrue(f.is_harvested)

    def test_good_and_bad_nc_zip(self):
        zip_file = make_zip(self.temp_dir, [GOOD_NC, BAD_NC])
        handler = self.handler_class(zip_file,
                                     include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                     check_params={'checks': ['cf', 'imos:1.4']}
                                     )
        handler.run()

        self.assertIsInstance(handler.error, ComplianceCheckFailedError)
        self.assertEqual(len(handler.file_collection), 2)

        coll_dict = {f.name: f for f in handler.file_collection}
        f_good = coll_dict[os.path.basename(GOOD_NC)]
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
        handler = self.handler_class(zip_file,
                                     include_regexes=['IMOS_ANMN-NRS_.*\.(nc|pdf|png|cnv)'],
                                     check_params={'checks': ['cf', 'imos:1.4']}
                                     )
        handler.run()
        self.assertEqual(len(handler.file_collection), 4)


if __name__ == '__main__':
    unittest.main()
