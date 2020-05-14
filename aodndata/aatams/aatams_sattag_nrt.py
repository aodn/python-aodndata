"""The AATAMS_SATTAG_QC_NRT handler."""
import os
import logging
from aodncore.pipeline import (
    HandlerBase,
    PipelineFilePublishType,
    FileType,
    PipelineFile,
)
from aodncore.pipeline.files import RemotePipelineFileCollection
from aodncore.pipeline.exceptions import InvalidFileContentError

from .aatams_sattag_qc_dm_schema import (
    AatamsSattagQcDmSchema,
)  # schema is the same as dm

logger = logging.getLogger(__name__)

# AATAMS NRT global constants
AATAMS_SATTAG_QC_NRT_BASE = "IMOS/AATAMS/AATAMS_SATTAG_QC_NRT"


def metadata_index(file_list):
    """Locate the metadata.csv file in a multi value PipelineFile object."""
    fname = [x for x in file_list if "metadata" in x.name]
    return list(file_list).index(fname[0])


def dest_path(filepath):
    return os.path.join(AATAMS_SATTAG_QC_NRT_BASE, os.path.basename(filepath))


class AatamsSattagQcNRTHandler(HandlerBase):
    """The class for aatams sattag qc NRT."""

    def __init__(self, *args, **kwargs):
        """Initialize the class by only accepting zip files."""
        super(AatamsSattagQcNRTHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = [".zip"]
        self.allowed_regexes = ["^.+_nrt\\.zip$"]
        self.allowed_archive_path_regexes = [AATAMS_SATTAG_QC_NRT_BASE + ".+\\.zip"]
        self.allowed_dest_path_regexes = [AATAMS_SATTAG_QC_NRT_BASE + ".+\\.csv"]
        self.dest_path_function = dest_path
        self.archive_input_file = True
        self.archive_path_function = self.dest_path_function

        # Initialize the schema class and set default validation method
        self.schema = AatamsSattagQcDmSchema()  # Schema is the same as dm
        self.validation_call = self.schema.extensive_validation
        # Use below to just validate the file names and csv headers
        # self.validation_call = self.SCHEMA.quick_validation
        self.previous_files = None

    def is_update_required(self, old_metadata_file):
        """Check if updates to the dataset/archive are required by inspecting the most
        recent dates between the new stream and remote(current) metadata state."""
        new_valid_data = self.schema.metadata
        new_recent_date = sorted(new_valid_data["qc_end_date"])[-1]

        _, old_valid_data = self.schema.validate_file(old_metadata_file)
        old_recent_date = sorted(old_valid_data["qc_end_date"])[-1]
        return new_recent_date > old_recent_date

    def preprocess(self):
        """Validate individual files within the zip."""
        files_in_zip = self.file_collection.get_attribute_list("local_path")
        self.validation_call(files_in_zip)

        self.input_file_object.publish_type = PipelineFilePublishType.ARCHIVE_ONLY

        self.file_collection.filter_by_attribute_value(
            "file_type", FileType.CSV,
        ).set_publish_types(PipelineFilePublishType.HARVEST_UPLOAD)

    # TODO enable below and test for removal of old NRT files
    # def process(self):
    #     """Process NRT files, removing the previous files if content of new file is
    #     updated."""

    #     self.previous_files = self.state_query.query_storage(dest_path(""))
    #     if self.previous_files:
    #         old_metadata_file = self.previous_files[metadata_index(self.previous_files)]
    #         new_metadata_file = self.file_collection[
    #             metadata_index(self.file_collection)
    #         ]
    #         logger.info("NRT update requested: Comparing timestamps in the metadata files %s and %s", old_metadata_file, new_metadata_file)
    #         remote_collection = RemotePipelineFileCollection(old_metadata_file)
    #         self.state_query.download(remote_collection)
    #         if self.is_update_required(old_metadata_file.local_path):
    #             for remote_file in self.previous_files:
    #                 filename = remote_file.name
    #                 file_to_remove = PipelineFile(
    #                     filename, is_deletion=True, dest_path=dest_path(filename),
    #                 )
    #                 file_to_remove.publish_type = (
    #                     PipelineFilePublishType.DELETE_UNHARVEST
    #                 )
    #                 self.file_collection.add(file_to_remove)
    #         else:
    #             raise InvalidFileContentError(
    #                 "File %s within %s contains older entries than current NRT state from %s"
    #                 % (
    #                     new_metadata_file.name,
    #                     self.input_file_object.name,
    #                     old_metadata_file.name,
    #                 ),
    #             )
