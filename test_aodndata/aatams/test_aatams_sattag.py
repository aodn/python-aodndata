"""Tests for the AATAMS DM and NRT streams."""
import os
import unittest
from testfixtures import LogCapture
from schema import SchemaError
from aodncore.pipeline import FileType, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileContentError
from aodncore.util import TemporaryDirectory
from aodncore.testlib import make_zip, HandlerTestCase
from aodndata.aatams.aatams_sattag import (
    AatamsSattagQcNrtHandler,
    AatamsSattagQcDmHandler,
    AATAMS_SATTAG_QC_DM_BASE,
    AATAMS_SATTAG_QC_NRT_BASE,
    NRT_TIMESTAMP_COMPARISON_MSG,
)
from aodndata.aatams.aatams_sattag_schema import CSV_LONGITUDE

TEST_ROOT = os.path.join(os.path.dirname(__file__))

DM_GOOD_ZIP = os.path.join(TEST_ROOT, "simple_dm.zip")
DM_SINGLE_CSV = os.path.join(TEST_ROOT, "metadata_ct111_dm.csv")
DM_INVALID_LONGITUDE = os.path.join(TEST_ROOT, "invalidlongitude_dm.zip")

NRT_FIRST_ZIP = os.path.join(TEST_ROOT, "first_nrt_batch", "ct155_nrt.zip")
NRT_SECOND_ZIP = os.path.join(TEST_ROOT, "second_nrt_batch", "ct155_nrt.zip")
NRT_NEW_CAMPAIGN = os.path.join(TEST_ROOT, "new_ct156_nrt.zip")
NRT_SINGLE_CSV = os.path.join(TEST_ROOT, "metadata_ct111_nrt.csv")
NRT_EMPTY_DIVE_ZIP = os.path.join(TEST_ROOT, "emptydive_ct999_nrt.zip")
NRT_MIXED_CAMPAIGN = os.path.join(TEST_ROOT, "mixcampaign_ct555_nrt.zip")
NRT_CSV_CAMPAIGN_MISMATCH = os.path.join(TEST_ROOT, "csvcampaignmismatch_ct999_nrt.zip")
NRT_CSV_CAMPAIGN_FILE_CONTENT_MISMATCH = os.path.join(TEST_ROOT, "csvfilecontentmismatch_ct156_nrt.zip")



def check_file(cls, file):
    """Check if a file is a valid AATAMS file with correct storage options."""
    if file.file_type is FileType.CSV:
        cls.assertFalse(file.should_store and file.should_archive and file.is_stored and file.is_archived)
        cls.assertTrue(file.is_harvested)
    elif file.file_type is FileType.ZIP:
        cls.assertTrue(file.should_store)
        cls.assertEqual(cls.base_path, os.path.dirname(file.dest_path))
    else:
        raise ValueError("File {local_path} not a Zip or CSV".format(local_path=file.local_path))


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

    def test_fail_single_dm_csv_input(self):
        """Checking single DM csv ingestion."""
        handler = self.run_handler_with_exception(SchemaError, DM_SINGLE_CSV)
        self.assertEqual(handler.file_collection[0].dest_path, None)

    def test_fail_zip_with_single_csv_input(self):
        """Single csv in zip should fail."""
        valid_zip_name = 'xxx_dm.zip'
        with TemporaryDirectory() as tmpdir:
            zipfile = make_zip(tmpdir, [DM_SINGLE_CSV])
            valid_zip_name = os.path.join(os.path.dirname(zipfile), 'xxx_dm.zip')
            os.rename(zipfile, valid_zip_name)
            self.run_handler_with_exception(SchemaError, valid_zip_name)

    def test_harvest_dm_csvs_in_zip(self):
        """Checking ingestion of valid DM zipfile."""
        handler = self.run_handler(DM_GOOD_ZIP)
        check_file(self, handler.input_file_object)
        for file in handler.file_collection:
            check_file(self, file)

    def test_invalid_longitude(self):
        """Checking if invalid longitude will raise a proper msg"""
        with LogCapture() as log:
            handler = self.run_handler_with_exception(SchemaError,DM_INVALID_LONGITUDE)
            all_msgs = [x.getMessage() for x in log.records]

            expected_error_msg = CSV_LONGITUDE._error
            found_error_msg = False
            for msg in all_msgs:
                if expected_error_msg in msg:
                    found_error_msg = True
                    error = msg
            assert(found_error_msg)

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

    def test_fail_single_nrt_csv_input(self):
        """Checking single NRT csv ingestion."""
        handler = self.run_handler_with_exception(SchemaError, NRT_SINGLE_CSV)
        self.assertEqual(handler.file_collection[0].dest_path, None)

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
            old_zip_file = [x for x in handler.file_collection if NRT_FIRST_ZIP in x.src_path][0]

            handler = self.run_handler(NRT_SECOND_ZIP)
            for file in handler.file_collection:
                self.check_file(file)
            new_metadata_file = handler.get_file(handler.file_collection, 'metadata')

            all_msgs = [x.getMessage() for x in log.records]
            timestamp_msg = NRT_TIMESTAMP_COMPARISON_MSG.format(
                old_zip_file.dest_path, new_metadata_file.src_path,
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

    def test_empty_dive_csv(self):
        """Allow an empty dive file case to be ingested and updated"""
        self.run_handler(NRT_EMPTY_DIVE_ZIP)

    def test_stream_update(self):
        """Test stream of sequential updates for different campaigns
        and storage state afterwards"""
        self.run_handler(NRT_FIRST_ZIP)
        self.run_handler(NRT_FIRST_ZIP)
        self.run_handler(NRT_SECOND_ZIP)
        self.run_handler(NRT_SECOND_ZIP)
        self.run_handler(NRT_NEW_CAMPAIGN)
        self.run_handler(NRT_NEW_CAMPAIGN)
        self.run_handler(NRT_EMPTY_DIVE_ZIP)
        handler = self.run_handler(NRT_EMPTY_DIVE_ZIP)
        handler_dest_path = handler.dest_path_function("")
        expected = {os.path.basename(x) for x in [NRT_FIRST_ZIP, NRT_NEW_CAMPAIGN, NRT_EMPTY_DIVE_ZIP]}
        result = {os.path.basename(x.dest_path) for x in handler.state_query.query_storage(handler_dest_path)}
        self.assertEqual(result, expected)

    def test_mixmatch_campaign(self):
        """Test a bad zip with multiple campaigns csv filenames"""
        self.run_handler_with_exception(SchemaError, NRT_MIXED_CAMPAIGN)

    def test_csv_campaign_mismatch(self):
        """Test a bad zip file with consistent campaign filenames but inconsistent csv campaign content"""
        self.run_handler_with_exception(SchemaError, NRT_CSV_CAMPAIGN_MISMATCH)

    def test_csv_campaign_mismatch_in_content(self):
        """Test a bad zip file with matching campaign names but unmatched csv campaign content"""
        self.run_handler_with_exception(SchemaError, NRT_CSV_CAMPAIGN_FILE_CONTENT_MISMATCH)


if __name__ == "__main__":
    unittest.main()
