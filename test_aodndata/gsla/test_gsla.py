import os
import shutil
import unittest
from unittest.mock import patch
from aodncore.util import TemporaryDirectory

from aodncore.pipeline import PipelineFilePublishType, FileType, PipelineFile, PipelineFileCollection, \
    PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileFormatError, InvalidFileNameError, AttributeValidationError
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase
from aodncore.util.misc import get_pattern_subgroups_from_string

from aodndata.gsla.handler import GslaHandler, GSLA_PREFIX_PATH, GSLA_REGEX

TEST_ROOT = os.path.join(os.path.dirname(__file__))

GOOD_NC_NRT = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20220101T000000Z_GSLA_FV02_NRT.nc")
GOOD_NC_DM02 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20000101T000000Z_GSLA_FV02_DM02.nc")

GOOD_YEARLY_FILE_DM02 = os.path.join(TEST_ROOT, 'IMOS_OceanCurrent_HV_2018.nc')

BAD_PATH = os.path.join(TEST_ROOT, 'bad.nc')


class TestGslaHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = GslaHandler
        super(TestGslaHandler, self).setUp()

    def test_good_nc(self):
        """ check various good dest_path """
        dest_path = GslaHandler.dest_path(GOOD_NC_NRT)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "NRT/2022", os.path.basename(GOOD_NC_NRT))
        self.assertEqual(expected_path, dest_path)

        dest_path = GslaHandler.dest_path(GOOD_NC_DM02)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/2000", os.path.basename(GOOD_NC_DM02))
        self.assertEqual(expected_path, dest_path)

        dest_path = GslaHandler.dest_path(GOOD_YEARLY_FILE_DM02)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/yearfiles", os.path.basename(GOOD_YEARLY_FILE_DM02))
        self.assertEqual(expected_path, dest_path)

    def test_bad_file(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_PATH)

    @patch('aodndata.gsla.handler.GSLA_PREFIX_PATH', 'BAD/STORAGE')
    def test_bad_prefix(self):
        """ test case to add allowed_dest_path_regexes to json"""
        self.run_handler_with_exception(AttributeValidationError,
                                        GOOD_NC_DM02,
                                        allowed_dest_path_regexes=["IMOS/OceanCurrent/GSLA"])

    def test_get_fields(self):
        """ test basic function outputs"""
        fields = get_pattern_subgroups_from_string(os.path.basename(GOOD_NC_DM02), GSLA_REGEX)
        self.assertEqual(fields['nc_time_cov_start'], '20000101T000000Z')
        self.assertEqual(fields['product_type'], 'DM02')

    def test_good_dm02(self):
        handler = self.run_handler(GOOD_NC_DM02,
                                   check_params={'checks': ['cf:1.6', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f_nc = handler.file_collection.filter_by_attribute_value('file_type', FileType.NETCDF)[0]

        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f_nc.name, os.path.basename(GOOD_NC_DM02))

        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/2000", os.path.basename(GOOD_NC_DM02))
        self.assertEqual(expected_path, f_nc.dest_path)

    def test_push_yearly_file(self):
        """
        Test case: Push new yearly file *.nc with UPLOAD_ONLY
        """
        # run the handler
        handler = self.run_handler(GOOD_YEARLY_FILE_DM02)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

if __name__ == '__main__':
    unittest.main()
