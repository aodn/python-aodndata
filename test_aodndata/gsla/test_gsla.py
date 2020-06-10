import gzip
import os
import shutil
import unittest
from unittest.mock import patch
from datetime import datetime

from aodncore.pipeline import PipelineFilePublishType, FileType, PipelineFile, PipelineFileCollection, \
    PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileFormatError, InvalidFileNameError, AttributeValidationError
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase
from aodncore.util.misc import get_pattern_subgroups_from_string

from aodndata.gsla.handler import GslaHandler, GSLA_PREFIX_PATH, GSLA_REGEX, get_creation_date

TEST_ROOT = os.path.join(os.path.dirname(__file__))


GOOD_NC_DM00 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_19930101T000000Z_GSLA_FV02_DM00_C-20130913T082343Z.nc.gz")
GOOD_NC_NRT00 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20180101T000000Z_GSLA_FV02_NRT00_C-20180105T222006Z.nc.gz")
GOOD_NC_DM01 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_20000101T000000Z_GSLA_FV02_DM01_C-20200601T010724Z.nc.gz")

GOOD_YEARLY_FILE_DM00 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_2018_C-20180806T000000Z.nc.gz")
GOOD_YEARLY_FILE_DM01 = os.path.join(TEST_ROOT, "IMOS_OceanCurrent_HV_2018_C-20181025T000000Z.nc.gz")

PREV_YEARLY_NC_STORAGE = os.path.join(TEST_ROOT, 'IMOS_OceanCurrent_HV_2018_C-20180801T000000Z.nc.gz')
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
        """ check various good dest_path """
        dest_path = GslaHandler.dest_path(GOOD_NC_DM00)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM00/1993", os.path.basename(GOOD_NC_DM00))
        self.assertEqual(expected_path, dest_path)

        dest_path = GslaHandler.dest_path(GOOD_NC_NRT00)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "NRT00/2018", os.path.basename(GOOD_NC_NRT00))
        self.assertEqual(expected_path, dest_path)

        dest_path = GslaHandler.dest_path(GOOD_NC_DM01)
        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM01/2000", os.path.basename(GOOD_NC_DM01))
        self.assertEqual(expected_path, dest_path)

        # for YEARLY_FILES, the dest_path will need to read the global attributes to find the product_type. In this case
        # since we're only testing the dest_path function and not the hanlder. we're ungzipping the gz
        nc_file_gunzip_path = os.path.join(self.temp_dir, os.path.basename(GOOD_YEARLY_FILE_DM00.rstrip('.gz')))
        with open(os.path.join(self.temp_dir, os.path.basename(GOOD_YEARLY_FILE_DM00.rstrip('.gz'))), "wb") as tmp:
            shutil.copyfileobj(gzip.open(GOOD_YEARLY_FILE_DM00), tmp)
            dest_path = GslaHandler.dest_path(nc_file_gunzip_path)
            expected_path = os.path.join(GSLA_PREFIX_PATH, "DM00/yearfiles", os.path.basename(GOOD_YEARLY_FILE_DM00))
            self.assertEqual(expected_path, dest_path)

        # DM01
        nc_file_gunzip_path = os.path.join(self.temp_dir, os.path.basename(GOOD_YEARLY_FILE_DM01.rstrip('.gz')))
        with open(os.path.join(self.temp_dir, os.path.basename(GOOD_YEARLY_FILE_DM01.rstrip('.gz'))), "wb") as tmp:
            shutil.copyfileobj(gzip.open(GOOD_YEARLY_FILE_DM01), tmp)
            dest_path = GslaHandler.dest_path(nc_file_gunzip_path)
            expected_path = os.path.join(GSLA_PREFIX_PATH, "DM01/yearfiles", os.path.basename(GOOD_YEARLY_FILE_DM01))
            self.assertEqual(expected_path, dest_path)

    def test_bad_file(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_PATH)

    @patch('aodndata.gsla.handler.GSLA_PREFIX_PATH', 'BAD/STORAGE')
    def test_bad_prefix(self):
        """ test case to add allowed_dest_path_regexes to json"""
        self.run_handler_with_exception(AttributeValidationError,
                                        PREV_NC_STORAGE,
                                        allowed_dest_path_regexes=["IMOS/OceanCurrent/GSLA"])

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

        yearly_creation_date = get_creation_date(GOOD_YEARLY_FILE_DM00)
        self.assertEqual(yearly_creation_date, datetime(2018, 8, 6, 0, 0, 0))

        with self.assertRaises(InvalidFileNameError):
            _ = get_creation_date('not_a_real_path')

    def test_good_dm01(self):
        handler = self.run_handler(GOOD_NC_DM01,
                                   check_params={'checks': ['cf', 'imos:1.4']}
                                   )
        self.assertEqual(len(handler.file_collection), 2)
        f_nc = handler.file_collection.filter_by_attribute_value('file_type', FileType.NETCDF)[0]
        f_gz = handler.file_collection.filter_by_attribute_value('file_type', FileType.GZIP)[0]

        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.NO_ACTION)
        self.assertEqual(f_gz.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f_gz.name, os.path.basename(GOOD_NC_DM01))

        expected_path = os.path.join(GSLA_PREFIX_PATH, "DM01/2000", os.path.basename(GOOD_NC_DM01))
        self.assertEqual(expected_path, f_gz.dest_path)

    def test_setup_upload_location_push_newer_file(self):
        """
        Test case: Check creation date of incoming *.nc.gz is newer that one already on storage
                   HARVEST_UPLOAD the incoming *.nc.gz
                   DELETE_UNHARVEST the previous *.nc.gz
                   NO_ACTION on the nc inside the *.nc.gz
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
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.NO_ACTION)

        nc_gz_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        self.assertEqual(nc_gz_file.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)

        nc_gz_delete = handler.file_collection.filter_by_attribute_value('name', os.path.basename(PREV_NC_STORAGE))[0]
        self.assertEqual(nc_gz_delete.publish_type, PipelineFilePublishType.DELETE_UNHARVEST)

    def test_setup_upload_location_push_same_file(self):
        """
        Test case: Push same file twice to $INCOMING_DIR
                   HARVEST_UPLOAD the incoming *.nc.gz
                   NO_ACTION on the nc inside the *.nc.gz
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

        # run the handler by uploading again the same file
        handler = self.run_handler(PREV_NC_STORAGE)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.NO_ACTION)

        nc_gz_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        self.assertEqual(nc_gz_file.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)

    @patch('aodndata.gsla.handler.GSLA_PREFIX_PATH', 'BAD/PREFIX')
    def test_setup_upload_location_push_newer_file_bad_prefix(self):
        """
        Test case: Check creation date of incoming *.nc.gz is newer that one already on storage
                   HARVEST_UPLOAD the content of the *nc.gz

                   BUT check THAT
                   We don't delete files not starting with a good value of GSLA_PREFIX_PATH.
                   In our case we patch this global variable to empty to check this
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(PREV_NC_STORAGE, dest_path=os.path.join('IMOS/OceanCurrent/GSLA/DM00/2018/',
                                                                             os.path.basename(PREV_NC_STORAGE)))

        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # run the handler
        self.run_handler_with_exception(AttributeValidationError,
                                        NEWER_CREATION_DATE_NC,
                                        allowed_dest_path_regexes=["IMOS/OceanCurrent/GSLA"])

    def test_setup_upload_location_push_older_file(self):
        """
        Test case: Check creation date of incoming *.nc.gz is older that one already on storage
                   NO_ACTION  *nc.gz
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

        # run the handler on the new file with an older creation date
        self.run_handler_with_exception(InvalidFileNameError, OLDER_CREATION_DATE_NC)

    def test_push_yearly_file(self):
        """
        Test case: Push new yearly file *.nc.gz with UPLOAD_ONLY
        """
        # run the handler
        handler = self.run_handler(GOOD_YEARLY_FILE_DM00)

        nc_gz_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        self.assertEqual(nc_gz_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.NO_ACTION)

    def test_setup_upload_location_push_newer_yearly_file(self):
        """
        Test case: Check creation date of incoming  yearly *.nc.gz is newer that one already on storage
                   UPLOAD_ONLY the new incoming *.nc.gz
                   DELETE_ONLY the previous *.nc.gz
                   NO_ACTION on the nc inside the *.nc.gz
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(PREV_YEARLY_NC_STORAGE, dest_path=os.path.join(
            'IMOS/OceanCurrent/GSLA/DM00/yearfiles',
            os.path.basename(PREV_YEARLY_NC_STORAGE)))

        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # run the handler
        handler = self.run_handler(GOOD_YEARLY_FILE_DM00)

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.NO_ACTION)

        nc_gz_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        self.assertEqual(nc_gz_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        nc_gz_delete = handler.file_collection.filter_by_attribute_value('name', os.path.basename(PREV_YEARLY_NC_STORAGE))[0]
        self.assertEqual(nc_gz_delete.publish_type, PipelineFilePublishType.DELETE_ONLY)


if __name__ == '__main__':
    unittest.main()
