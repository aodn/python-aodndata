from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest
import shutil
from datetime import datetime, timedelta
from netCDF4 import Dataset

from aodncore.pipeline import PipelineFilePublishType, PipelineFile, PipelineFileCollection, FileType
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileNameError, InvalidFileContentError
from aodncore.pipeline.storage import get_storage_broker
from aodncore.util.misc import get_pattern_subgroups_from_string
from aodndata.acorn.handler import AcornHandler, ACORN_FILE_PATTERN, get_creation_date
from aodncore.testlib import HandlerTestCase

TEST_ROOT = os.path.join(os.path.dirname(__file__))

GOOD_NC_FV00 = os.path.join(TEST_ROOT,
                       'IMOS_ACORN_V_20180501T003000Z_ROT_FV00_1-hour-avg.nc')

GOOD_NC_FV01 = os.path.join(TEST_ROOT,
                       'IMOS_ACORN_V_20170101T003000Z_ROT_FV01_1-hour-avg.nc')

NON_INDEX_NC = os.path.join(TEST_ROOT,
                            'IMOS_ACORN_V_20101201T050000Z_BONC_FV00_sea-state.nc')


BAD_FILES = ('IMOS_ACON_RV_20171014T060000Z_LANC_FV00_radial.nc',
             'IMOS_ACORN_RV_201611203000Z_GUI_FV00_radial.nc',
             'IMOS_ACORN_V_20180910T010000Z_BONC_FV00_sea-se.nc',
             'IMOS_ACORN_RV_20120507T053500Z_FV01_radial.nc',
             'IMOS_ACORN_RV_20191014T192000Z_TAN_FV01_radial.nc.some_suffix',
             'prefix.IMOS_ACORN_RV_20191014T192000Z_TAN_FV01_radial.nc')


class TestAcornHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AcornHandler
        super(TestAcornHandler, self).setUp()

    def test_good_netcdf_generic_fv00(self):
        handler = self.run_handler(GOOD_NC_FV00,
                                   include_regexes=['IMOS_ACORN_.*\.nc']
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]

        self.assertEqual(f.dest_path, os.path.join('IMOS/ACORN/gridded_1h-avg-current-map_non-QC/ROT/2018/05/01',
                                                   os.path.basename(GOOD_NC_FV00)))
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)
        
    def test_fv00_in_dm(self):
        # check that a FV00 file is not allowed in DM folder/pipeline
        # mock JSON file by adding allowed_regexes & allowed_dest_path_regexes
        self.run_handler_with_exception(InvalidInputFileError, GOOD_NC_FV00,
                                        allowed_regexes=[
                                            '^IMOS_ACORN_[A-Z].*_[0-9]{8}T[0-9]{6}Z_[A-Z]{3,4}_FV01_(radial|sea-state|wavespec|windp|wavep|1-hour-avg)\.nc$'],
                                        allowed_dest_path_regexes=["^IMOS/ACORN/.*FV01.*\.nc$"]
                                        )

    def test_fv01_in_rt(self):
        # check that a FV01 file is not allowed in RT folder/pipeline
        # mock JSON file by adding allowed_regexes & allowed_dest_path_regexes
        self.run_handler_with_exception(InvalidInputFileError, GOOD_NC_FV01,
                                        allowed_regexes=[
                                            '^IMOS_ACORN_[A-Z].*_[0-9]{8}T[0-9]{6}Z_[A-Z]{3,4}_FV00_(radial|sea-state|wavespec|windp|wavep|1-hour-avg)\.nc$'],
                                        allowed_dest_path_regexes=["^IMOS/ACORN/.*FV00.*\.nc$"]
                                        )

    def test_non_index_netcdf(self):
        handler = self.run_handler(NON_INDEX_NC,
                                   include_regexes=['IMOS_ACORN_.*\.nc']
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        self.assertEqual(f.dest_path, os.path.join('IMOS/ACORN/vector/BONC/2010/12/01',
                                                   os.path.basename(NON_INDEX_NC)))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_created_date(self):
        self.assertEqual(get_creation_date(GOOD_NC_FV00), datetime(2018, 5, 1, 1, 5, 3))

    def test_get_fields_from_filename(self):
        filename = os.path.basename(GOOD_NC_FV00)
        fields = get_pattern_subgroups_from_string(filename, ACORN_FILE_PATTERN)

        self.assertEqual(fields['data_parameter_code'], 'V')
        self.assertEqual(fields['platform_code'], 'ROT')
        self.assertEqual(fields['product_type'], '1-hour-avg')

    def test_bad_bc(self):
        for nc_file in BAD_FILES:
            with self.assertRaises(InvalidFileNameError):
                AcornHandler.dest_path(nc_file)

    def test_setup_upload_location_push_file_older_creation_date(self):
        """
        Test case: Check creation date of new *.nc is older that one already on storage
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(GOOD_NC_FV01, dest_path=AcornHandler.dest_path(GOOD_NC_FV01))
        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # create a new file based on GOOD_NC_FV01. Modify it with an older creation date
        nc_file_old_creation_date_path = os.path.join(self.temp_dir, os.path.basename(GOOD_NC_FV01))
        shutil.copyfile(GOOD_NC_FV01, nc_file_old_creation_date_path)
        with Dataset(nc_file_old_creation_date_path, mode='r+') as nc_obj:
            delta_time = timedelta(1, 1, 1)
            new_time = datetime.strptime(nc_obj.date_created, '%Y-%m-%dT%H:%M:%SZ') - delta_time
            nc_obj.date_created = datetime.strftime(new_time, '%Y-%m-%dT%H:%M:%SZ')

        # run the handler on the new file with an older creation date
        handler = self.handler_class(nc_file_old_creation_date_path, include_regexes=['IMOS_ACORN_.*\.nc'])
        handler.opendap_root = broker.prefix
        handler.run()

        self.assertIsInstance(handler.error, InvalidFileContentError)

    def test_setup_upload_location_push_file_newer_creation_date(self):
        """
        Test case: Check creation date of new *.nc is newer that one already on storage
        """
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file = PipelineFile(GOOD_NC_FV01,
                                     dest_path=AcornHandler.dest_path(GOOD_NC_FV01))
        preexisting_files.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # create a new file based on GOOD_NC_FV01. Modify it with an newer creation date
        # we patch the global variable from the handler in order to use the temporary broker file
        nc_file_new_creation_date_path = os.path.join(self.temp_dir, os.path.basename(GOOD_NC_FV01))
        shutil.copyfile(GOOD_NC_FV01, nc_file_new_creation_date_path)
        with Dataset(nc_file_new_creation_date_path, mode='r+') as nc_obj:
            delta_time = timedelta(1, 1, 1)
            new_time = datetime.strptime(nc_obj.date_created, '%Y-%m-%dT%H:%M:%SZ') + delta_time
            nc_obj.date_created = datetime.strftime(new_time, '%Y-%m-%dT%H:%M:%SZ')

        # run the handler on the new file with an newer creation date
        handler = self.handler_class(nc_file_new_creation_date_path, include_regexes=['IMOS_ACORN_.*\.nc'])
        handler.opendap_root = broker.prefix
        handler.run()

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)


if __name__ == '__main__':
    unittest.main()
