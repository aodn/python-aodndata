import os
import unittest
import zipfile

from aodncore.pipeline import PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileContentError
from aodncore.testlib import HandlerTestCase

from aodndata.nsw_oeh.handler import NswOehHandler, NSWOEHSurveyProcesor, is_date, check_crs, get_name_fields, \
    get_survey_name, get_survey_methods

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_MB_ZIP = os.path.join(TEST_ROOT, 'NSWOEH_20151029_PortHackingBateBay_MB.zip')
BAD_MB_ZIP = os.path.join(TEST_ROOT, 'NSWOEH_20170601_BadSurvey_MB.zip')
GOOD_STAX_ZIP = os.path.join(TEST_ROOT, 'NSWOEH_20111125_KingscliffBeach_STAX.zip')
BAD_STAX_ZIP = os.path.join(TEST_ROOT, 'NSWOEH_20170602_BadSurvey_STAX.zip')
CORRUPTED_SHP_ZIP = os.path.join(TEST_ROOT, 'NSWOEH_20111111_Corrupted_SHP.zip')


def get_shp_path(zipfile_path):
    """Return the path of a coverage shapefile (_SHP.shp) within a zip file"""

    with zipfile.ZipFile(zipfile_path) as zf:
        path_list = zf.namelist()
    paths = [path for path in path_list if path.endswith('_SHP.shp')]

    assert len(paths) == 1, "Expected exactly 1 shapefile in zip, found {n}".format(n=len(paths))

    return '/' + paths[0]


class TestNswOehHandler(HandlerTestCase):
    proc = NSWOEHSurveyProcesor

    def setUp(self):
        self.handler_class = NswOehHandler
        super(TestNswOehHandler, self).setUp()

    def test_is_date(self):
        self.assertTrue(is_date('20170601'))
        self.assertFalse(is_date('170601'))
        self.assertFalse(is_date('June2017'))
        self.assertFalse(is_date('2017-06-01'))
        self.assertFalse(is_date('17/06/01'))

    def test_check_crs(self):
        for crs in ('W84Z55', 'W84Z56'):
            self.assertListEqual(check_crs(crs), [])
        for crs in ('', 'NONE', 'W84Z42'):
            self.assertEqual(len(check_crs(crs)), 1)

    def test_get_name_fields(self):
        in_fld = ['one', 'two', 'three']
        fld, ext = get_name_fields('_'.join(in_fld))
        self.assertListEqual(in_fld, fld)
        self.assertEqual('', ext)

        in_fld = ['NSWOEH', '20151029', 'PortHackingBateBay', 'MB']
        in_ext = 'zip'
        fld, ext = get_name_fields('_'.join(in_fld) + '.' + in_ext)
        self.assertListEqual(in_fld, fld)
        self.assertEqual(in_ext, ext)

    def test_get_survey_name(self):
        self.assertEqual('20151029_PortHackingBateBay',
                         get_survey_name('NSWOEH_20151029_PortHackingBateBay_MB.shp'))
        self.assertEqual('20120921_TweedRiver',
                         get_survey_name('NSWOEH_20120921_TweedRiver_STAX_SHP.cpg'))
        self.assertEqual('', get_survey_name('NOT_NSWOEH_file.zip'))

    def test_get_survey_methods(self):
        self.assertEqual('MB', get_survey_methods('NSWOEH_20151029_PortHackingBateBay_MB.shp'))
        self.assertEqual('STAX', get_survey_methods('NSWOEH_20120921_TweedRiver_STAX_SHP.cpg'))
        self.assertEqual('', get_survey_methods('NOT_NSWOEH_file.zip'))
        self.assertEqual('', get_survey_methods('NSWOEH_file_bad.zip'))
        self.assertEqual('', get_survey_methods('NSWOEH_0151029_PortHackingBateBay_XYZ.zip'))

    def test_check_name_good_mb(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        good_names = ['NSWOEH_20151029_PortHackingBateBay_MB.zip',
                      'NSWOEH_20151029_PortHackingBateBay_MB_ScientificRigour.pdf',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.CPG',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.dbf',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.prj',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.sbn',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.sbx',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.shp',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.shp.xml',
                      'NSWOEH_20151029_PortHackingBateBay_MB_SHP.shx',
                      'NSWOEH_20151029_PortHackingBateBay_MB_BKSGRD001GSS_W84Z56GRY_FLD744_20151221_FV02.sd',
                      'NSWOEH_20151029_PortHackingBateBay_MB_BKSGRD001GSS_W84Z56GRY_FLD744_20151221_FV02.tiff',
                      'NSWOEH_20151029_PortHackingBateBay_MB_BTYGRD002GSS_W84Z56AHD_FLD744_20151223_FV02.tif',
                      'NSWOEH_20151029_PortHackingBateBay_MB_BKSGRD002GSS_W84Z56GRY_FLD744_20151221_FV02.xya',
                      'NSWOEH_20151029_PortHackingBateBay_MB_BTYGRD002GSS_W84Z56AHD_FLD744_20151221_FV02.xyz'
                      ]
        for name in good_names:
            msg = pz.check_name(name)
            self.assertEqual([], msg, "Unexpected messages for {name}:\n{msg}".format(name=name, msg=msg))

    def test_check_name_wrong_date(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(['Wrong survey date 20011111 (zip file name has 20151029)'],
                         pz.check_name('NSWOEH_20011111_PortHackingBateBay_MB_SHP.shx')
                         )

    def test_check_name_wrong_location(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(['Wrong location TweedRiver (zip file name has PortHackingBateBay)'],
                         pz.check_name('NSWOEH_20151029_TweedRiver_MB_SHP.shx')
                         )

    def test_check_name_wrong_method(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(["Wrong survey method code STAX, expected MB"],
                         pz.check_name('NSWOEH_20151029_PortHackingBateBay_STAX_ScientificRigour.pdf')
                         )

    def test_check_name_short(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(["File name should have at least 4 underscore-separated fields."],
                         pz.check_name('NSWOEH_20151029_PortHackingBateBay.zip')
                         )

    def test_check_name_bad_method(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(["Field 4 should be a valid survey method code"],
                         pz.check_name('NSWOEH_20151029_PortHackingBateBay_BBB.zip')
                         )
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_STAX.zip')
        self.assertEqual(["Field 4 should be a valid survey method code"],
                         pz.check_name('NSWOEH_20151029_PortHackingBateBay_BBB.zip')
                         )

    def test_check_name_bad_rigour(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(["Unknown extension 'doc'",
                          "The Scientific Rigour (metadata) sheet must be in PDF format."],
                         pz.check_name('NSWOEH_20151029_PortHackingBateBay_MB_ScientificRigour.doc')
                         )

    def test_check_name_all_bad(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertCountEqual(pz.check_name('IMOS_170202_N0-name_BBB.what'),
                              ["File name must start with 'NSWOEH'",
                               "Field 2 should be a valid date (YYYYMMDD).",
                               "Field 3 should be a location code consisting only of letters.",
                               "Field 4 should be a valid survey method code",
                               "Unknown extension 'what'",
                               "File name should have at least 5 underscore-separated fields."]
                              )

    # TODO: unittests for fields beyond the first 4

    def test_check_name_good_stax(self):
        pz = self.proc('NSWOEH_20111125_KingscliffBeach_STAX.zip')
        good_names = ['NSWOEH_20111125_KingscliffBeach_STAX_SHP.shx',
                      'NSWOEH_20111125_KingscliffBeach_STAX_RV12_AHD_MGA56_SEPT2012_TINMODEL_COVERAGE.dbf',
                      'NSWOEH_20111125_KingscliffBeach_STAX_2012_09_OEH_TWEED_RIVER_SURVEY.zip',
                      'NSWOEH_20111125_KingscliffBeach_STAX_56873s01.pdf',
                      'NSWOEH_20111125_KingscliffBeach_STAX_KingscliffBeach2011_AHD_MGA.xyz',
                      'NSWOEH_20111125_KingscliffBeach_STAX_KingscliffBeach2011.TXT',
                      'NSWOEH_20111125_KingscliffBeach_STAX_KingscliffBeach2011_AHD_MGA.sbn',
                      'NSWOEH_20111125_KingscliffBeach_STAX_log',
                      'NSWOEH_20111125_KingscliffBeach_STAX_schema.ini'
                      ]
        for name in good_names:
            msg = pz.check_name(name)
            self.assertEqual([], msg, "Unexpected messages for {name}:\n{msg}".format(name=name, msg=msg))

    def test_check_name_bad_stax(self):
        pz = self.proc('NSWOEH_20111125_KingscliffBeach_STAX.zip')
        self.assertCountEqual(pz.check_name('IMOS_170202_N0-name_BBB.what'),
                              ["File name must start with 'NSWOEH'",
                               "Field 2 should be a valid date (YYYYMMDD).",
                               "Field 3 should be a location code consisting only of letters.",
                               "Field 4 should be a valid survey method code"]
                              )

    def test_check_name_spaces(self):
        pz = self.proc('NSWOEH_20120921_TweedRiver_STAX')
        self.assertEqual(
            pz.check_name('NSWOEH_20120921_TweedRiver_STAX_2012_09 OEH TWEED RIVER SURVEY.xyz'),
            ["File name should not contain spaces"]
        )

    def test_good_shapefile(self):
        pz = self.proc(GOOD_MB_ZIP)
        shp_path = get_shp_path(GOOD_MB_ZIP)
        self.assertEqual([], pz.check_shapefile(shp_path))

    def test_bad_shapefile(self):
        pz = self.proc(BAD_MB_ZIP)
        shp_path = get_shp_path(BAD_MB_ZIP)
        self.assertNotEqual([], pz.check_shapefile(shp_path))

    def test_corrupted_shapefile(self):
        pz = self.proc(CORRUPTED_SHP_ZIP)
        shp_path = get_shp_path(CORRUPTED_SHP_ZIP)
        msg = pz.check_shapefile(shp_path)
        self.assertEqual(1, len(msg))
        self.assertTrue(msg[0].startswith("Unable to open shapefile"))

    def test_check_all_good_mb(self):
        pz = self.proc(GOOD_MB_ZIP)
        self.assertDictEqual(pz.check_all(), dict())

    def test_check_all_good_stax(self):
        pz = self.proc(GOOD_STAX_ZIP)
        self.assertDictEqual(pz.check_all(), dict())

    def test_check_all_bad_mb(self):
        pz = self.proc(BAD_MB_ZIP)
        report = pz.check_all()
        self.assertCountEqual(report["Zip file contents"], ["Missing bathymetry xyz file"])
        self.assertCountEqual(report["NSWOEH_20151029_PortHackingBateBay_MB_ScientificRigour.pdf"],
                              ["Wrong survey date 20151029 (zip file name has 20170601)",
                               "Wrong location PortHackingBateBay (zip file name has BadSurvey)"
                               ]
                              )

    def test_check_all_bad_stax(self):
        pz = self.proc(BAD_STAX_ZIP)
        report = pz.check_all()
        self.assertCountEqual(report["Zip file contents"],
                              ["Missing metadata file (PDF format)",
                               "Missing survey coverage shapefile"]
                              )
        self.assertCountEqual(report["NSWOEH_20111125_KingscliffBeach_STAX_schema.ini"],
                              ["Wrong survey date 20111125 (zip file name has 20170602)",
                               "Wrong location KingscliffBeach (zip file name has BadSurvey)"
                               ]
                              )

    def test_get_dest_path(self):
        pz = self.proc('NSWOEH_20151029_PortHackingBateBay_MB.zip')
        self.assertEqual(pz.get_dest_path(), 'NSW-OEH/Multi-beam/2015/20151029_PortHackingBateBay')
        pz = self.proc('NSWOEH_20111125_KingscliffBeach_STAX.zip')
        self.assertEqual(pz.get_dest_path(), 'NSW-OEH/Single-beam/2011/20111125_KingscliffBeach')

    def test_get_dest_path_bad(self):
        pz = self.proc('NOTHING_GOOD.zip')
        with self.assertRaises(ValueError):
            pz.get_dest_path()

    def test_good_mb(self):
        handler = self.run_handler(GOOD_MB_ZIP)

        dest_path_base = 'NSW-OEH/Multi-beam/2015/20151029_PortHackingBateBay/'

        with zipfile.ZipFile(GOOD_MB_ZIP) as zf:
            expected_files = {os.path.basename(p) for p in zf.namelist() if not p.endswith('/')}
        expected_dest_paths = {os.path.join(dest_path_base, p) for p in expected_files}
        result_dest_paths = {f for f in handler.file_collection.get_attribute_list('dest_path') if f}
        self.assertSetEqual(expected_dest_paths, result_dest_paths)

        file_collection_harvest_upload = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                                        PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(10, len(file_collection_harvest_upload._PipelineFileCollection__s.item_list))
        for f in file_collection_harvest_upload:
            self.assertTrue(f.is_harvested)
            self.assertTrue(f.is_stored)
            self.assertEqual(f.dest_path, dest_path_base + os.path.basename(f.src_path))

        self.assertTrue(PipelineFilePublishType.NO_ACTION, handler.file_collection.filter_by_attribute_id('publish_type',
                                                                                        PipelineFilePublishType.NO_ACTION))

    def test_bad_mb(self):
        self.run_handler_with_exception(InvalidFileContentError, BAD_MB_ZIP)

    def test_good_stax(self):
        handler = self.run_handler(GOOD_STAX_ZIP)

        dest_path_base = 'NSW-OEH/Single-beam/2011/20111125_KingscliffBeach/'

        with zipfile.ZipFile(GOOD_STAX_ZIP) as zf:
            expected_files = {os.path.basename(p) for p in zf.namelist() if '_STAX_SHP.' in p}
        expected_files.add(os.path.basename(GOOD_STAX_ZIP))
        expected_dest_paths = {os.path.join(dest_path_base, p) for p in expected_files}
        result_dest_paths = {f for f in handler.file_collection.get_attribute_list('dest_path') if f}

        self.assertSetEqual(expected_dest_paths, result_dest_paths)
        self.assertEqual(1, len(handler.file_collection.filter_by_attribute_id('publish_type',
                                                                               PipelineFilePublishType.UPLOAD_ONLY).
                                _PipelineFileCollection__s.item_list))

        file_collection_harvest_upload = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                                        PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(8, len(file_collection_harvest_upload._PipelineFileCollection__s.item_list))
        for f in file_collection_harvest_upload:
            self.assertTrue(f.is_harvested)
            self.assertTrue(f.is_stored)
            self.assertEqual(f.dest_path, os.path.join(dest_path_base, os.path.basename(f.src_path)))

    def test_bad_stax(self):
        self.run_handler_with_exception(InvalidFileContentError, BAD_STAX_ZIP)


if __name__ == '__main__':
    unittest.main()
