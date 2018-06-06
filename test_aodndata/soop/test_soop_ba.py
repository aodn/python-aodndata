import os
import unittest

from aodncore.pipeline import PipelineFilePublishType, FileType, PipelineFile, PipelineFileCollection
from aodncore.testlib import HandlerTestCase
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileContentError
from aodndata.soop.soop_ba import SoopBaHandler
from aodncore.pipeline.storage import get_storage_broker

TEST_ROOT = os.path.join(os.path.dirname(__file__))
PREV_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-BA_A_20160116T152139Z_VKAD_FV02_Antarctic-Discovery'
                       '-ES60-38_END-20160129T062056Z_C-20160101T000000Z.nc')
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-BA_A_20160116T152139Z_VKAD_FV02_Antarctic-Discovery'
                       '-ES60-38_END-20160129T062056Z_C-20170227T055245Z.nc')
BAD_NC = os.path.join(TEST_ROOT,
                      'IMOS_SOOP-BA_A_20160116T152139Z_VKAD_FV02_Antarctic-Discovery'
                      '-ES60-38_END-20160129T062056Z_C-20170227T055245Z_BAD.nc')
GOOD_ZIP = os.path.join(TEST_ROOT, 'Antarctic-Discovery_20160116-20160129.zip')
BAD_ZIP = os.path.join(TEST_ROOT, 'Antarctic-Discovery_20160116-20160129_BAD.zip')
CSV = os.path.join(TEST_ROOT, 'Antarctic_Discovery_20160115-20160129_test.gps.csv')


class TestSoopBaHandler(HandlerTestCase):
    """It is recommended to inherit from the HandlerTestCase class (which is itself a subclass of the standard
       unittest.TestCase class). This provides some useful methods and properties to shortcut some common test
       scenarios.
    """

    # This is a "boilerplate" method that must appear in each test case
    #  in order to correctly inherit from the HandlerTestCase class
    def setUp(self):
        # set the handler_class attribute to your handler (as imported above)
        self.handler_class = SoopBaHandler
        super(TestSoopBaHandler, self).setUp()

    def test_good_ba_file(self):
        # we expect this to succeed, so if the handler experiences an error, it is considered a
        # "failed test"
        handler = self.run_handler(GOOD_NC)

        f = handler.file_collection[0]
        # self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-BA/VKAD_Antarctic-Discovery/Antarctic-Discovery_20160116-20160129/'
                         + f.name)
        self.assertTrue(f.is_stored)

    def test_good_nc_zip(self):
        handler = self.run_handler(GOOD_ZIP)
        nc_files = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        f = nc_files[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-BA/VKAD_Antarctic-Discovery/Antarctic-Discovery_20160116-20160129/' + f.name
                         )

        png = handler.file_collection.filter_by_attribute_value('extension', '.png')
        p = png[0]
        self.assertEqual(p.dest_path,
                         'IMOS/SOOP/SOOP-BA/VKAD_Antarctic-Discovery/Antarctic-Discovery_20160116-20160129/' + p.name)
        self.assertEqual(p.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        rawf = handler.file_collection.filter_by_attribute_value('extension', '.raw')
        raw = rawf[0]
        self.assertEqual(raw.archive_path,
                         'IMOS/SOOP/SOOP-BA/raw/VKAD_Antarctic-Discovery/Antarctic-Discovery_20160116-20160129/'
                         + raw.name)
        self.assertEqual(raw.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)

    def test_bad_zip(self):
        """ test with missing netcdf in ZIP archive"""
        self.run_handler_with_exception(InvalidInputFileError, BAD_ZIP)

    def test_bad_nc(self):
        """Test with invalid netcdf missing a report_id"""
        self.run_handler_with_exception(InvalidFileContentError, BAD_NC)

    def test_setup_upload_location(self):
        # create some PipelineFiles to represent the existing files on 'S3'
        preexisting_files = PipelineFileCollection()

        existing_file1 = PipelineFile(PREV_NC, dest_path=os.path.join(
            'IMOS/SOOP/SOOP-BA/VKAD_Antarctic-Discovery/Antarctic-Discovery_20160116-20160129/',
            os.path.basename(PREV_NC)))

        existing_file2 = PipelineFile(CSV, dest_path=os.path.join(
            'IMOS/SOOP/SOOP-BA/VKAD_Antarctic-Discovery/Antarctic-Discovery_20160116-20160129/',
            os.path.basename(CSV)))
        preexisting_files.update([existing_file1, existing_file2])

        # set the files to UPLOAD_ONLY
        preexisting_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_files)

        # run the handler
        handler = self.run_handler(GOOD_ZIP)

        # add some tests to make sure the previous files were handled appropriately, e.g.
        # - they were added as deletions
        # - they were successfully deleted
        # - they were the *only* ones deleted
        nc_files = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        for nc in nc_files:
            if nc.name == os.path.basename(PREV_NC):
                self.assertEqual(nc.publish_type, PipelineFilePublishType.DELETE_UNHARVEST)
                self.assertEqual(nc.is_deleted, True)
            else:
                self.assertEqual(nc.is_deleted, False)
        csvs = handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV)
        for csv in csvs:
            if csv.name == os.path.basename(CSV):
                self.assertEqual(csv.publish_type, PipelineFilePublishType.DELETE_ONLY)
                self.assertEqual(csv.is_deleted, True)
            else:
                self.assertEqual(csv.is_deleted, False)

        png = handler.file_collection.filter_by_attribute_id('file_type', FileType.PNG)
        self.assertEqual(png[0].is_deleted, False)

        if __name__ == '__main__':
            unittest.main()
