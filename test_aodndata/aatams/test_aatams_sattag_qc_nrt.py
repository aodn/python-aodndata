import os
import unittest
import shutil

from aodncore.pipeline import FileType
from aodncore.testlib import HandlerTestCase
from aodndata.aatams.aatams_sattag_nrt import AatamsSattagQcNRTHandler
from aodncore.pipeline.exceptions import InvalidInputFileError,InvalidFileContentError
from aodncore.testlib import NullStorageBroker

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_ZIP = os.path.join(TEST_ROOT, "first_nrt.zip")
NEXT_ZIP = os.path.join(TEST_ROOT, "second_nrt.zip")
BAD_ZIP = os.path.join(TEST_ROOT, "simple_zip.zip")
AATAMS_SATTAG_NRT_BASE = "IMOS/AATAMS/AATAMS_SATTAG_QC_NRT"


class TestAatamsNRTHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AatamsSattagQcNRTHandler
        super(TestAatamsNRTHandler, self).setUp()

    def move_file_to_download_folder(self, file):
        shutil.move(file, self.temp_dir)

    def test_avoid_non_nrt_pickup(self):
        self.run_handler_with_exception(InvalidInputFileError, BAD_ZIP)

    def test_harvest_csvs_in_zip(self):
        handler = self.run_handler(GOOD_ZIP)
        for file in handler.file_collection:
            if file.file_type is FileType.CSV:
                self.assertEqual(
                    AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.dest_path)
                )
                self.assertTrue(file.is_harvested and file.is_stored)
            elif file.file_type is FileType.ZIP:
                self.assertEqual(
                    AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.archive_path),
                )
                self.assertTrue(file.is_archived)

    #TODO enable tests below when removal of old nrt is required
    #def test_removal_of_old_file_is_triggered(self):

    #    handler = self.run_handler(GOOD_ZIP)
    #    for file in handler.file_collection:
    #        if file.file_type is FileType.CSV:
    #            self.assertEqual(
    #                AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.dest_path)
    #            )
    #            self.assertTrue(file.is_harvested and file.is_stored)
    #        elif file.file_type is FileType.ZIP:
    #            self.assertEqual(
    #                AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.archive_path),
    #            )
    #            self.assertTrue(file.is_archived)

    #    #overwrite the broker with NullStorageBroker
    #    self.broker = NullStorageBroker(self.temp_dir)
    #    handler = self.run_handler(NEXT_ZIP)
    #    for file in handler.file_collection:
    #        if file.file_type is FileType.CSV:
    #            self.assertEqual(
    #                AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.dest_path)
    #            )
    #            self.assertTrue(file.is_harvested and file.is_stored)
    #        elif file.file_type is FileType.ZIP:
    #            self.assertEqual(
    #                AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.archive_path),
    #            )
    #            self.assertTrue(file.is_archived)

    #def test_removal_of_old_file_is_not_triggered(self):

    #    handler = self.run_handler(GOOD_ZIP)
    #    for file in handler.file_collection:
    #        if file.file_type is FileType.CSV:
    #            self.assertEqual(
    #                AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.dest_path)
    #            )
    #            self.assertTrue(file.is_harvested and file.is_stored)
    #        elif file.file_type is FileType.ZIP:
    #            self.assertEqual(
    #                AATAMS_SATTAG_NRT_BASE, os.path.dirname(file.archive_path),
    #            )
    #            self.assertTrue(file.is_archived)

    #    #overwrite the broker with NullStorageBroker
    #    self.broker = NullStorageBroker(self.temp_dir)
    #    self.run_handler_with_exception(InvalidFileContentError, GOOD_ZIP)



if __name__ == "__main__":
    unittest.main()
