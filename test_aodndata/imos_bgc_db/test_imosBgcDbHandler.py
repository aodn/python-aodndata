import os
import os
import unittest
from unittest.mock import patch

from aodncore.pipeline import (PipelineFileCheckType, FileType)
from aodncore.testlib import HandlerTestCase

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
            "name": "bgc_phyto_raw",
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


class TestImosBgcDbHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = ImosBgcDbHandler
        super().setUp()

    @patch('aodncore.pipeline.steps.harvest.CsvHarvesterRunner')
    def test_good_csv(self, mock_harvester):
        handler = self.run_handler(GOOD_CSV, harvest_params=HARVEST_PARAMS)

        self.assertEqual(handler.harvest_type, 'csv')
        self.assertTrue(handler.input_file_object.is_archived)
        for f in handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV):
            self.assertTrue(f.is_checked)
            self.assertIs(f.check_type, PipelineFileCheckType.TABLE_SCHEMA_CHECK)

        self.assertTrue(mock_harvester.called)


if __name__ == '__main__':
    unittest.main()
