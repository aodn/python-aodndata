import gzip
import os
import shutil
import unittest
from unittest.mock import patch
from aodncore.util import TemporaryDirectory
import tempfile

from aodncore.pipeline import PipelineFilePublishType, FileType, PipelineFile, PipelineFileCollection, \
    PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileFormatError, InvalidFileNameError, AttributeValidationError
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase
from aodncore.util.misc import get_pattern_subgroups_from_string

from aodndata.gsla.handler import GslaHandler, GSLA_PREFIX_PATH, GSLA_REGEX

TEST_ROOT = os.path.join(os.path.dirname(__file__))

GOOD_NC_GZ_DM02_nc = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20000101T000000Z_GSLA_FV02_DM02.nc.gz")
GOOD_NC_GZ_NRT = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20220101T000000Z_GSLA_FV02_NRT.nc.gz")
GOOD_NC_GZ_DM02 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20230101T000000Z_GSLA_FV02_DM02.nc.gz")

GOOD_YEARLY_FILE_DM02 = os.path.join(TEST_ROOT, 'IMOS_OceanCurrent_HV_2018.nc.gz')

BAD_PATH = os.path.join(TEST_ROOT, 'bad.nc.gz')


class TestGslaHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = GslaHandler
        super(TestGslaHandler, self).setUp()

    def test_push_unzipped_nc(self):
        """ check on pushing *.nc rather than *.nc.gz """

        with TemporaryDirectory() as tmpdir:
            with gzip.open(GOOD_NC_GZ_DM02_nc, 'rb') as f_in:
                good_nc_dm01 = os.path.join(tmpdir, os.path.basename(GOOD_NC_GZ_DM02_nc.replace('.gz', '')))
                with open(good_nc_dm01, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

        handler = self.run_handler(good_nc_dm01,
                                   check_params={'checks': ['cf:1.6', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 2)
        f_nc = handler.file_collection.filter_by_attribute_value('file_type', FileType.NETCDF)[0]
        f_gz = handler.file_collection.filter_by_attribute_value('file_type', FileType.GZIP)[0]

        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.NO_ACTION)
        self.assertEqual(f_gz.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)

        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/2000", os.path.basename(GOOD_NC_GZ_DM02_nc))
        self.assertEqual(expected_path, f_gz.dest_path)


    def test_good_nc(self):
        """ check various good dest_path """
        dest_path = GslaHandler.dest_path(GOOD_NC_GZ_NRT)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "NRT/2022", os.path.basename(GOOD_NC_GZ_NRT))
        self.assertEqual(expected_path, dest_path)

        dest_path = GslaHandler.dest_path(GOOD_NC_GZ_DM02)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/2023", os.path.basename(GOOD_NC_GZ_DM02))
        self.assertEqual(expected_path, dest_path)

        dest_path = GslaHandler.dest_path(GOOD_NC_GZ_DM02_nc)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/2000", os.path.basename(GOOD_NC_GZ_DM02_nc))
        self.assertEqual(expected_path, dest_path)

        # for YEARLY_FILES, the dest_path will need to read the global attributes to find the product_type. In this case
        # since we're only testing the dest_path function and not the hanlder. we're ungzipping the gz
        nc_file_gunzip_path = os.path.join(self.temp_dir, os.path.basename(GOOD_YEARLY_FILE_DM02.rstrip('.gz')))
        with open(os.path.join(self.temp_dir, os.path.basename(GOOD_YEARLY_FILE_DM02.rstrip('.gz'))), "wb") as tmp:
            shutil.copyfileobj(gzip.open(GOOD_YEARLY_FILE_DM02), tmp)
            dest_path = GslaHandler.dest_path(nc_file_gunzip_path)
            expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/yearfiles", os.path.basename(GOOD_YEARLY_FILE_DM02))
            self.assertEqual(expected_path, dest_path)

    def test_bad_file(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_PATH)

    @patch('aodndata.gsla.handler.GSLA_PREFIX_PATH', 'BAD/STORAGE')
    def test_bad_prefix(self):
        """ test case to add allowed_dest_path_regexes to json"""
        self.run_handler_with_exception(AttributeValidationError,
                                        GOOD_NC_GZ_DM02_nc,
                                        allowed_dest_path_regexes=["IMOS/OceanCurrent/GSLA"])

    def test_get_fields(self):
        """ test basic function outputs"""
        fields = get_pattern_subgroups_from_string(os.path.basename(GOOD_NC_GZ_DM02_nc), GSLA_REGEX)
        self.assertEqual(fields['nc_time_cov_start'], '20000101T000000Z')
        self.assertEqual(fields['product_type'], 'DM02')

    def test_good_dm01(self):
        handler = self.run_handler(GOOD_NC_GZ_DM02_nc,
                                   check_params={'checks': ['cf:1.6', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 2)
        f_nc = handler.file_collection.filter_by_attribute_value('file_type', FileType.NETCDF)[0]
        f_gz = handler.file_collection.filter_by_attribute_value('file_type', FileType.GZIP)[0]

        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.NO_ACTION)
        self.assertEqual(f_gz.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f_gz.name, os.path.basename(GOOD_NC_GZ_DM02_nc))

        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM/2000", os.path.basename(GOOD_NC_GZ_DM02_nc))
        self.assertEqual(expected_path, f_gz.dest_path)

    def test_push_yearly_file(self):
        """
        Test case: Push new yearly file *.nc.gz with UPLOAD_ONLY
        """
        # run the handler
        handler = self.run_handler(GOOD_YEARLY_FILE_DM02)

        nc_gz_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        self.assertEqual(nc_gz_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.NO_ACTION)


if __name__ == '__main__':
    unittest.main()
