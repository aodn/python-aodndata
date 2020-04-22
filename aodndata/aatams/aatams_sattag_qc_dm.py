"""The AATAMS_SATTAG_QC_DM handler."""
import os

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType
from .aatams_sattag_qc_dm_schema import AatamsSattagQcDmSchema

# AATAMS DM global constants
AATAMS_SATTAG_QC_DM_BASE = "IMOS/AATAMS/AATAMS_SATTAG_QC_DM"


def dest_path(filepath):
    return os.path.join(AATAMS_SATTAG_QC_DM_BASE, os.path.basename(filepath))


class AatamsSattagQcDmHandler(HandlerBase):
    """The class for aatams sattag qc dm."""

    def __init__(self, *args, **kwargs):
        """Initialize the class by only accepting zip files."""
        super(AatamsSattagQcDmHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = [".zip"]
        self.allowed_regexes = ["^.+_.+$"]
        self.allowed_archive_path_regexes = [AATAMS_SATTAG_QC_DM_BASE + ".+\\.zip"]
        self.allowed_dest_path_regexes = [AATAMS_SATTAG_QC_DM_BASE + ".+\\.csv"]
        self.dest_path_function = dest_path
        self.archive_input_file = True
        self.archive_path_function = self.dest_path_function

        # Initialize the schema class and set default validation method
        self.schema = AatamsSattagQcDmSchema()
        self.validation_call = self.schema.extensive_validation
        # Use below to just validate the file names and csv headers
        # self.validation_call = self.SCHEMA.quick_validation

    def preprocess(self):
        """Validate individual files within the zip."""
        files_in_zip = self.file_collection.get_attribute_list('local_path')
        self.validation_call(files_in_zip)

        self.file_collection.add(self.input_file)
        self.file_collection.filter_by_attribute_id(
            "file_type", FileType.ZIP,
        ).set_publish_types(PipelineFilePublishType.ARCHIVE_ONLY)

        self.file_collection.filter_by_attribute_value(
            "file_type", FileType.CSV,
        ).set_publish_types(PipelineFilePublishType.HARVEST_UPLOAD)
