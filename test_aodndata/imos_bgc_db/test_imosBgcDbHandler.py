import os
import unittest
from shutil import copyfile
from unittest.mock import patch

from aodncore.pipeline import (PipelineFileCheckType, PipelineFilePublishType, FileType)
from aodncore.pipeline.configlib import LazyConfigManager
from aodncore.pipeline.exceptions import ComplianceCheckFailedError
from aodncore.testlib import HandlerTestCase
from aodncore.testlib.testutil import load_runtime_patched_pipeline_config_file, TESTLIB_CONF_DIR

from aodndata.imos_bgc_db.handler import ImosBgcDbHandler

HARVEST_PARAMS = {
    "db_schema": "imos_bgc_db",
    "ingest_type": "replace",
    "db_objects": [
        {
            "name": "bgc_trip",
            "type": "table"
        },
        {
            "name": "bgc_phyto_changelog",
            "type": "table"
        },
        {
            "name": "bgc_phytoplankton_map",
            "type": "materialized view",
            "dependencies": ["bgc_trip"]
        },
    ]
}

TEST_ROOT = os.path.dirname(__file__)
GOOD_CSV = os.path.join(TEST_ROOT, 'bgc_trip.csv')
GOOD_ZIP = os.path.join(TEST_ROOT, 'bgc_phyto_test.zip')


class TestImosBgcDbHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = ImosBgcDbHandler
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
        self.assertTrue(handler.input_file_object.is_archived)
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV):
            self.assertIs(f.check_type, PipelineFileCheckType.TABLE_SCHEMA_CHECK)
            self.assertIs(f.publish_type, PipelineFilePublishType.HARVEST_ONLY)
            self.assertTrue(f.is_checked)
            self.assertFalse(f.is_stored)

        self.assertTrue(mock_harvester.called)

    @patch('aodncore.pipeline.steps.harvest.CsvHarvesterRunner')
    def test_good_zip(self, mock_harvester):
        handler = self.run_handler(GOOD_ZIP, harvest_params=HARVEST_PARAMS, config=self.testconfig)

        self.assertEqual(handler.harvest_type, 'csv')
        self.assertTrue(handler.input_file_object.is_archived)
        self.assertEqual(len(handler.file_collection), 2)
        for f in handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV):
            self.assertIs(f.check_type, PipelineFileCheckType.TABLE_SCHEMA_CHECK)
            self.assertIs(f.publish_type, PipelineFilePublishType.HARVEST_ONLY)
            self.assertTrue(f.is_checked)
            self.assertFalse(f.is_stored)

        self.assertTrue(mock_harvester.called)

    def test_unmatched_csv(self):
        unmatched_csv = os.path.join(self.temp_dir, 'unmatched.csv')
        copyfile(GOOD_CSV, unmatched_csv)

        self.run_handler_with_exception(ComplianceCheckFailedError, unmatched_csv,
                                        harvest_params=HARVEST_PARAMS, config=self.testconfig
                                        )

    def test_invalid_csv(self):
        invalid_csv = os.path.join(self.temp_dir, 'bgc_trip.csv')
        copyfile(os.path.join(TEST_ROOT, 'bgc_trip_bad.csv'), invalid_csv)

        self.run_handler_with_exception(ComplianceCheckFailedError, invalid_csv,
                                        harvest_params=HARVEST_PARAMS, config=self.testconfig
                                        )


if __name__ == '__main__':
    unittest.main()
