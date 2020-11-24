"""Tests for the NRMN files."""
# check zip file and how many csv files are in it
# check single csv file

import os
import re
import unittest

from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFileCheckType
# from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileContentError
from aodncore.testlib import HandlerTestCase
from aodndata.nrmn.handler import NrmnHandler

TEST_ROOT = "/home/anaberger/aodn/chef/src/tmp/NRMN"
# TEST_ROOT = os.path.join(os.path.dirname(__file__))

NRMN_GOOD_ZIP_BASENAME = "NRMN_public_endpoints.zip"
NRMN_GOOD_ZIP = os.path.join(TEST_ROOT, "NRMN_public_endpoints.zip")
NRMN_SINGLE_CSV = os.path.join(TEST_ROOT, "ep_m1_public.csv")


class TestNrmnHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = NrmnHandler
        super(TestNrmnHandler, self).setUp()

    def test_single_csv(self):
        """Checking single csv ingestion."""
        handler = self.run_handler(NRMN_SINGLE_CSV, include_regexes=[r'.*\.csv'])
        self.assertEqual(len(handler.file_collection), 1, 'It is a csv file!')

    def test_csv_filenames_pattern_in_zip(self):
        handler = self.run_handler(NRMN_GOOD_ZIP, include_regexes=[r'ep_.*\.csv'])
        self.assertEqual(len(handler.file_collection), 12, 'filenames pattern ok!')

    def test_harvest_csvs_in_zip(self):
        """Checking ingestion of valid .zip file with 12 .csv files in it"""
        base_path = "IMOS/NRMN"
        handler = self.run_handler(NRMN_GOOD_ZIP)
        self.assertEqual(12, len(handler.file_collection))
        for file in handler.file_collection:
            if file.file_type is FileType.CSV:
                self.assertTrue(file.is_harvested)
                self.assertFalse(file.is_stored)
                self.assertFalse(file.is_archived)


if __name__ == "__main__":
    unittest.main()
