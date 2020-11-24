"""Tests for the NRMN files."""
# check zip file and how many csv files are in it
# check single csv file

import os
import re
import unittest

from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileContentError
from aodncore.testlib import HandlerTestCase
from aodntdata.nrmn.handlers import NrmnHandler

TEST_ROOT = "/home/anaberger/aodn/chef/src/tmp/NRMN"
# TEST_ROOT = os.path.join(os.path.dirname(__file__))

NRMN_GOOD_ZIP = os.path.join(TEST_ROOT, "NRMN_public_endpoints.zip")
NRMN_SINGLE_CSV = os.path.join(TEST_ROOT, "ep_m1_public.csv")


class TestNrmnHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = NrmnHandler
        super(TestNrmnHandler, self).setUp()

    def check_file(cls, file):
        """Check if a file is a valid NRMN file."""
        if file.file_type is FileType.CSV:
            cls.assertEqual(
                cls.base_path, os.path.dirname(file.dest_path),
            )
            cls.assertTrue(file.is_harvested and file.is_stored)
        elif file.file_type is FileType.ZIP:
            cls.assertEqual(
                cls.base_path, os.path.dirname(file.archive_path),
            )
            cls.assertTrue(file.is_archived)
        else:
            raise ValueError("File {file} not a Zip or CSV", file=file)


# class TestAatamsQcDmHandler(HandlerTestCase):
#     """Tests for the DM pipeline."""
#
#     base_path = AATAMS_SATTAG_QC_DM_BASE
#     check_file = check_file
#
#     def setUp(self):
#         self.handler_class = AatamsSattagQcDmHandler
#         super(TestAatamsQcDmHandler, self).setUp()
#
#     def test_avoid_nrt_pickup(self):
#         """Checking if handling NRT files as DM raises Error."""
#         self.run_handler_with_exception(InvalidInputFileError, NRT_FIRST_ZIP)
#         self.run_handler_with_exception(InvalidInputFileError, NRT_SINGLE_CSV)
#
#     def test_single_dm_csv_input(self):
#         """Checking single DM csv ingestion."""
#         handler = self.run_handler(DM_SINGLE_CSV)
#         self.check_file(handler.file_collection[0])
#
#     def test_harvest_dm_csvs_in_zip(self):
#         """Checking ingestion of valid DM zipfile."""
#         handler = self.run_handler(DM_GOOD_ZIP)
#         for file in handler.file_collection:
#             if file.file_type is FileType.CSV:
#                 self.assertEqual(
#                     AATAMS_SATTAG_QC_DM_BASE, os.path.dirname(file.dest_path)
#                 )
#                 self.assertTrue(file.is_harvested and file.is_stored)
#             elif file.file_type is FileType.ZIP:
#                 self.assertEqual(
#                     AATAMS_SATTAG_QC_DM_BASE, os.path.dirname(file.archive_path),
#                 )
#                 self.assertTrue(file.is_archived)
#
#
# if __name__ == "__main__":
#     unittest.main()
