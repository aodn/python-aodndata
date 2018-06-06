import os
import unittest

from aodncore.testlib import HandlerTestCase
from aodncore.pipeline import PipelineFilePublishType, FileType, PipelineFile, PipelineFileCollection
from aodncore.pipeline.storage import get_storage_broker
from aodncore.pipeline.exceptions import InvalidFileFormatError, InvalidPathFunctionError, InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string

from aodndata.gsla.handler import GslaHandler, GSLA_PREFIX_PATH, GSLA_REGEX, get_creation_date

from datetime import datetime
from mock import patch

TEST_ROOT = os.path.join(os.path.dirname(__file__))


GOOD_NC_DM00 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_19930101T000000Z_GSLA_FV02_DM00_C-20130913T082343Z.nc.gz")
GOOD_NC_NRT00 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20180101T000000Z_GSLA_FV02_NRT00_C-20180105T222006Z.nc.gz")
GOOD_YEARLY_FILE = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_1993_C-20150521T030649Z.nc.gz")

PREV_NC_STORAGE = os.path.join(TEST_ROOT, 'IMOS_OceanCurrent_HV_20180101T000000Z_GSLA_FV02_DM00_C-20180130T224000Z.nc.gz')
NEWER_CREATION_DATE_NC = os.path.join(TEST_ROOT, 'IMOS_OceanCurrent_HV_20180101T000000Z_GSLA_FV02_DM00_C-20181231T225959Z.nc.gz')
OLDER_CREATION_DATE_NC = os.path.join(TEST_ROOT, 'IMOS_OceanCurrent_HV_20180101T000000Z_GSLA_FV02_DM00_C-20100101T000000Z.nc.gz')

NC_FILE = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20180101T000000Z_GSLA_FV02_DM00_C-20181231T225959Z.nc")

BAD_PATH = os.path.join(TEST_ROOT, 'bad.nc.gz')


class TestGslaHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = GslaHandler
        super(TestGslaHandler, self).setUp()

    def test_push_unzipped_nc(self):
        """ check on pushing *.nc rather than *.nc.gz """
        self.run_handler_with_exception(InvalidFileFormatError, NC_FILE)

    def test_good_nc(self):
        """ check various good dest_path        """
        dest_path = GslaHandler.dest_path(GOOD_NC_DM00)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM00/1993", os.path.basename(GOOD_NC_DM00))
        self.assertEqual(dest_path, expected_path)

        dest_path = GslaHandler.dest_path(GOOD_NC_NRT00)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "NRT00/2018", os.path.basename(GOOD_NC_NRT00))
        self.assertEqual(dest_path, expected_path)

        dest_path = GslaHandler.dest_path(GOOD_YEARLY_FILE)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM00/yearfiles", os.path.basename(GOOD_YEARLY_FILE))
        self.assertEqual(dest_path, expected_path)

    def test_bad_file(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_PATH)

    @patch('aodndata.gsla.handler.GSLA_PREFIX_PATH', '')
    def test_bad_prefix(self):
        """ test handler if we mock the global variable GSAL_PREFIX_PATH to empty string """
        self.run_handler_with_exception(InvalidPathFunctionError, NEWER_CREATION_DATE_NC)

    def test_get_fields(self):
        """ test basic function outputs"""
        fields = get_pattern_subgroups_from_string(os.path.basename(GOOD_NC_DM00), GSLA_REGEX)

        self.assertEqual(fields['nc_time_cov_start'], '19930101T000000Z')
        self.assertEqual(fields['creation_date'], '20130913T082343Z')
        self.assertEqual(fields['product_type'], 'DM00')

    def test_get_creation_date(self):
        """ test basic function outputs"""
        creation_date = get_creation_date(GOOD_NC_DM00)
        self.assertEqual(creation_date, datetime(2013, 9, 13, 8, 23, 43))

    def test_setup_upload_location_push_newer_file(self):
        """
        Test case: Check creation date of new *.nc.gz is newer that one is already on storage
                   HARVEST_ONLY the content of the *.gz (ie the *.nc)
                   PUBLISH_ONLY the *.nc.gz
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(PREV_NC_STORAGE, dest_path=os.path.join(
            'IMOS/OceanCurrent/GSLA/DM00/2018/',
            os.path.basename(PREV_NC_STORAGE)))

        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # run the handler
        handler = self.run_handler(NEWER_CREATION_DATE_NC)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.HARVEST_ONLY)

        nc_gz_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        self.assertEqual(nc_gz_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        nc_gz_delete = handler.file_collection.filter_by_attribute_value('name', os.path.basename(PREV_NC_STORAGE))[0]
        self.assertEqual(nc_gz_delete.publish_type, PipelineFilePublishType.DELETE_UNHARVEST)


    @patch('aodndata.gsla.handler.GSLA_PREFIX_PATH', '')
    def test_setup_upload_location_push_newer_file_bad_prefix(self):
        """
        Test case: Check creation date of new *.nc.gz is newer that one already on storage
                   HARVEST_ONLY the content of the *.gz
                   PUBLISH_ONLY the *.nc.gz

                   BUT check THAT
                   We don't delete files not starting with a good value of GSLA_PREFIX_PATH.
                   In our case we patch this global variable to empty to check this
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(PREV_NC_STORAGE, dest_path=os.path.join(
            'IMOS/OceanCurrent/GSLA/DM00/2018/',
            os.path.basename(PREV_NC_STORAGE)))

        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # run the handler
        self.run_handler_with_exception(InvalidPathFunctionError, NEWER_CREATION_DATE_NC)

    def test_setup_upload_location_push_older_file(self):
        """
        Test case: Check creation date of new *.nc.gz is newer that one already on storage
                   HARVEST_ONLY the content of the *.gz
                   PUBLISH_ONLY the *.nc.gz
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(PREV_NC_STORAGE, dest_path=os.path.join(
            'IMOS/OceanCurrent/GSLA/DM00/2018/',
            os.path.basename(PREV_NC_STORAGE)))

        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # run the handler
        handler = self.run_handler(OLDER_CREATION_DATE_NC)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.NO_ACTION)


if __name__ == '__main__':
    unittest.main()
