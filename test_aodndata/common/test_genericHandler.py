import os
import unittest

from aodncore.pipeline import PipelineFilePublishType
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodncore.testlib import HandlerTestCase
from aodndata.common.generic import GenericHandler
from aodndata.moorings.classifiers import dest_path_anmn_nrs_realtime

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NOT_NC = os.path.join(TEST_ROOT, 'not_a_netcdf_file.nc')
BAD_NC = os.path.join(TEST_ROOT, 'IMOS_ANMN-NRS_MT_20161109T231108Z_NRSMAI_FV00_NRSMAI-Surface-21-2016-11-MET-BAD.nc')
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_ANMN-NRS_MT_20161109T231108Z_NRSMAI_FV00_NRSMAI-Surface-21-2016-11-MET-realtime.nc')
INVALID_FILE = os.path.join(TEST_ROOT, 'invalid.png')
ZIP_FILE = os.path.join(TEST_ROOT, 'good_and_bad.zip')


class TestGenericHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = GenericHandler
        super(TestGenericHandler, self).setUp()

    def test_not_netcdf_nc_file(self):
        self.run_handler_with_exception(ComplianceCheckFailedError, NOT_NC)

    def test_no_dest_path(self):
        self.run_handler_with_exception(NotImplementedError, GOOD_NC)

    def test_noncompliant_netcdf(self):
        self.run_handler_with_exception(ComplianceCheckFailedError, BAD_NC,
                                        include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                        check_params={'checks': ['cf', 'imos:1.4']},
                                        dest_path_function=dest_path_anmn_nrs_realtime)

    def test_bad_name_netcdf(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_NC,
                                        include_regexes=['IMOS_ANMN-NRS_.*realtime\.nc'],
                                        dest_path_function=dest_path_anmn_nrs_realtime)

    def test_missing_attribute_for_dest_path(self):
        self.run_handler_with_exception(InvalidFileContentError, BAD_NC,
                                        include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                        dest_path_function=dest_path_anmn_nrs_realtime)

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                   include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']},
                                   dest_path_function=dest_path_anmn_nrs_realtime)

        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertEqual(f.name, os.path.basename(GOOD_NC))
            self.assertEqual(f.dest_path,
                             'IMOS/ANMN/NRS/REAL_TIME/NRSMAI/Meteorology/' + os.path.basename(GOOD_NC)
                             )

    def test_bad_zip(self):
        self.run_handler_with_exception(ComplianceCheckFailedError, ZIP_FILE,
                                        include_regexes=['IMOS_ANMN-NRS_.*\.nc'],
                                        check_params={'checks': ['cf', 'imos:1.3']},
                                        dest_path_function=dest_path_anmn_nrs_realtime)

    def test_good_zip(self):
        handler = self.run_handler(ZIP_FILE, dest_path_function='dest_path_testing')

        self.assertEqual(len(handler.file_collection), 2)
        for f in handler.file_collection:
            self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertIn(f.name, f.dest_path)
            self.assertTrue(f.is_harvested)
            self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
