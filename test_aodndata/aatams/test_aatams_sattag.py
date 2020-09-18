"""Tests for the AATAMS DM and NRT streams."""
import os
import unittest
from testfixtures import LogCapture
from aodncore.pipeline import FileType, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileContentError
from aodncore.testlib import HandlerTestCase
from aodndata.aatams.aatams_sattag import (
    AatamsSattagQcNrtHandler,
    AatamsSattagQcDmHandler,
    AATAMS_SATTAG_QC_DM_BASE,
    AATAMS_SATTAG_QC_NRT_BASE,
    NRT_TIMESTAMP_COMPARISON_MSG,
)

TEST_ROOT = os.path.join(os.path.dirname(__file__))

DM_GOOD_ZIP = os.path.join(TEST_ROOT, "simple_dm.zip")
DM_SINGLE_CSV = os.path.join(TEST_ROOT, "metadata_dm.csv")

NRT_FIRST_ZIP = os.path.join(TEST_ROOT, "first_nrt.zip")
NRT_SECOND_ZIP = os.path.join(TEST_ROOT, "second_nrt.zip")
NRT_NEW_CAMPAIGN = os.path.join(TEST_ROOT, "new_campaign_nrt.zip")
NRT_SINGLE_CSV = os.path.join(TEST_ROOT, "metadata_nrt.csv")


def check_file(cls, file):
    """Check if a file is a valid AATAMS file with correct storage options."""
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


class TestAatamsQcDmHandler(HandlerTestCase):
    """Tests for the DM pipeline."""

    base_path = AATAMS_SATTAG_QC_DM_BASE
    check_file = check_file

    def setUp(self):
        self.handler_class = AatamsSattagQcDmHandler
        super(TestAatamsQcDmHandler, self).setUp()

    def test_avoid_nrt_pickup(self):
        """Checking if handling NRT files as DM raises Error."""
        self.run_handler_with_exception(InvalidInputFileError, NRT_FIRST_ZIP)
        self.run_handler_with_exception(InvalidInputFileError, NRT_SINGLE_CSV)

    def test_single_dm_csv_input(self):
        """Checking single DM csv ingestion."""
        handler = self.run_handler(DM_SINGLE_CSV)
        self.check_file(handler.file_collection[0])

    def test_harvest_dm_csvs_in_zip(self):
        """Checking ingestion of valid DM zipfile."""
        handler = self.run_handler(DM_GOOD_ZIP)
        for file in handler.file_collection:
            if file.file_type is FileType.CSV:
                self.assertEqual(
                    AATAMS_SATTAG_QC_DM_BASE, os.path.dirname(file.dest_path)
                )
                self.assertTrue(file.is_harvested and file.is_stored)
            elif file.file_type is FileType.ZIP:
                self.assertEqual(
                    AATAMS_SATTAG_QC_DM_BASE, os.path.dirname(file.archive_path),
                )
                self.assertTrue(file.is_archived)


class TestAatamsQcNrtHandler(HandlerTestCase):
    """tests for the NRT pipeline."""

    base_path = AATAMS_SATTAG_QC_NRT_BASE
    check_file = check_file

    def setUp(self):
        self.handler_class = AatamsSattagQcNrtHandler
        super(TestAatamsQcNrtHandler, self).setUp()

    def test_avoid_dm_pickup(self):
        """Checking if handling DM files as NRT raises Error."""
        self.run_handler_with_exception(InvalidInputFileError, DM_GOOD_ZIP)
        self.run_handler_with_exception(InvalidInputFileError, DM_SINGLE_CSV)

    def test_single_nrt_csv_input(self):
        """Checking single NRT csv ingestion."""
        handler = self.run_handler(NRT_SINGLE_CSV)
        self.check_file(handler.file_collection[0])

    def test_harvest_csvs_in_zip(self):
        """Checking ingestion of valid NRT zipfile."""
        handler = self.run_handler(NRT_FIRST_ZIP)
        for file in handler.file_collection:
            check_file(self, file)

    def test_update_with_recent_file(self):
        """Checking if we can update the NRT state/archive with a more recent file."""
        with LogCapture() as log:
            handler = self.run_handler(NRT_FIRST_ZIP)
            for file in handler.file_collection:
                self.check_file(file)
            old_metadata_file = handler.get_metadata_file(handler.file_collection)

            handler = self.run_handler(NRT_SECOND_ZIP)
            for file in handler.file_collection:
                self.check_file(file)
            new_metadata_file = handler.get_metadata_file(handler.file_collection)

            all_msgs = [x.getMessage() for x in log.records]
            timestamp_msg = NRT_TIMESTAMP_COMPARISON_MSG.format(
                old_metadata_file.dest_path, new_metadata_file.src_path,
            )
            got_timestamp_msg = [x for x in all_msgs if timestamp_msg == x]
            self.assertFalse(got_timestamp_msg == [])
            self.assertListEqual(
                [],
                [
                    x.publish_type
                    for x in handler.file_collection
                    if x.publish_type == PipelineFilePublishType.DELETE_UNHARVEST
                ],
            )

    def test_block_old_files_replacing_new_ones(self):
        """Checking if we fail/block an older NRT file to be ingested."""
        handler = self.run_handler(NRT_SECOND_ZIP)
        for file in handler.file_collection:
            self.check_file(file)
        self.run_handler_with_exception(InvalidFileContentError, NRT_FIRST_ZIP)

    def test_no_clobber_if_different_campaign(self):
        """Only block nrt overwrite if it is the same campaign"""
        self.run_handler(NRT_SECOND_ZIP)
        self.run_handler(NRT_NEW_CAMPAIGN)  # older dates than above, but diff campaign


if __name__ == "__main__":
    unittest.main()
