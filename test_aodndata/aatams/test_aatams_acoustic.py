import os
from shutil import copyfile
from unittest.mock import patch

from aodncore.pipeline import (
    PipelineFileCheckType,
    PipelineFilePublishType,
    FileType)
from aodncore.pipeline.configlib import LazyConfigManager
from aodncore.pipeline.exceptions import (
    InvalidFileFormatError,
    InvalidFileNameError,
    ComplianceCheckFailedError,
    InvalidInputFileError
    )
from aodncore.testlib import HandlerTestCase
from aodncore.testlib.testutil import load_runtime_patched_pipeline_config_file, TESTLIB_CONF_DIR

from aodndata.aatams.aatams_acoustic import AnimalTrackingAcousticHandler

HARVEST_PARAMS = {
    "db_schema": "animal_tracking_acoustic_qc",
    "ingest_type": "replace",
    "db_objects": [
        {
            "name": "index_tmp",
            "type": "table"
        }
    ]
}

TEST_ROOT = os.path.dirname(__file__)
GOOD_CSV = os.path.join(TEST_ROOT, 'IMOS_ATF-ACOUSTIC_TAGID_A69-1602-11653_139644515_139644714.csv')
GOOD_ZIP = os.path.join(TEST_ROOT, 'IMOS_ATF-ACOUSTIC_ProjectBlah_good.zip')
BAD_CSV = os.path.join(TEST_ROOT, 'IMOS_ATF-ACOUSTIC_TAGID_A69-1602-11653_139644515_139644714_badschema.csv')
BAD_EXTENSION = os.path.join(TEST_ROOT, 'IMOS_ATF-ACOUSTIC_TAGID_A69-1602-11653_139644515_139644714.txt')
ZIP_NO_CSV = os.path.join(TEST_ROOT, 'IMOS_ATF-ACOUSTIC_ProjectBlah_no_csv.zip')

class TestAnimalTrackingAcousticHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AnimalTrackingAcousticHandler
        super().setUp()

        test_pipeline_config_file = os.path.join(TESTLIB_CONF_DIR, 'pipeline.conf')
        self.testconfig = LazyConfigManager()
        self.testconfig.__dict__['pipeline_config'] = load_runtime_patched_pipeline_config_file(
            test_pipeline_config_file, self.temp_dir, self.temp_dir,
            additional_patch={
                'harvester': {
                    "config_dir": TEST_ROOT,
                    "schema_base_dir": TEST_ROOT
                }
            }
        )

    @patch('aodncore.pipeline.steps.harvest.CsvHarvesterRunner')
    def test_good_csv(self, mock_harvester):
        handler = self.run_handler(GOOD_CSV, harvest_params=HARVEST_PARAMS, config=self.testconfig)

        self.assertEqual(handler.harvest_type, 'csv')
        self.assertEqual(len(handler.file_collection), 2)
        # check only the one data csv file GOOD_CSV
        f_tag = (handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV))[0]
        self.assertEqual(f_tag.name, os.path.basename(GOOD_CSV))
        self.assertIs(f_tag.check_type, PipelineFileCheckType.TABLE_SCHEMA_CHECK)
        self.assertIs(f_tag.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertTrue(f_tag.is_checked)
        self.assertTrue(f_tag.is_stored)
        # check that the index_tmp.csv is created, retrieving key metadata from GOOD_CSV
        f_index_tmp = (handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV)
                       .filter_by_attribute_regex('name', 'index_tmp.csv'))[0]
        self.assertIs(f_index_tmp.publish_type, PipelineFilePublishType.HARVEST_ONLY)
        self.assertTrue(mock_harvester.called)

    def test_bad_extension(self):
        """Testing a file with the wrong file extension"""
        self.run_handler_with_exception(InvalidFileFormatError, BAD_EXTENSION,
                                        harvest_params=HARVEST_PARAMS, config=self.testconfig
                                        )

    def test_bad_file_name(self):
        """Testing a file with a file name that doesn't match the regex"""
        bad_name = os.path.join(self.temp_dir, 'IMOS_AATAMS-ACOUSTIC_TAGID_A69-1602-11653_139644515_139644714.csv')
        copyfile(GOOD_CSV, bad_name)
        self.run_handler_with_exception(InvalidFileNameError, bad_name,
                                        harvest_params=HARVEST_PARAMS, config=self.testconfig
                                        )

    def test_bad_schema_csv(self):
        """This bad csv file includes missing required values and wrong datetime format
            Should not pass the schema check"""
        self.run_handler_with_exception(ComplianceCheckFailedError, BAD_CSV, harvest_params=HARVEST_PARAMS,
                                        config=self.testconfig
                                        )

    @patch('aodncore.pipeline.steps.harvest.CsvHarvesterRunner')
    def test_good_zip(self, mock_harvester):
        """
        Testing with multiple (3) valid csv files
        Ingests the number of valid csv + tmp_index (created during the pipeline process)
        Checks the number of files in the collection is as expected
        """
        handler = self.run_handler(GOOD_ZIP, harvest_params=HARVEST_PARAMS, config=self.testconfig)
        self.assertEqual(handler.harvest_type, 'csv')
        self.assertEqual(len(handler.file_collection), 4)
        self.assertTrue(mock_harvester.called)

    def test_empty_zip(self):
        empty_zip = os.path.join(self.temp_dir, 'empty_zip.zip')
        self.run_handler_with_exception(InvalidInputFileError, empty_zip,
                                        harvest_params=HARVEST_PARAMS, config=self.testconfig
                                        )

    def test_zip_with_no_csv(self):
        self.run_handler_with_exception(InvalidFileNameError, ZIP_NO_CSV,
                                        harvest_params=HARVEST_PARAMS, config=self.testconfig
                                        )
