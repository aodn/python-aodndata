"""A generic AATAMS_SATTAG handler."""
import os
import logging
from functools import partial
from aodncore.pipeline import (
    HandlerBase,
    PipelineFilePublishType,
    FileType,
    PipelineFile,
)
from aodncore.pipeline.files import RemotePipelineFileCollection
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileFormatError
from aodncore.util import extract_zip
from .aatams_sattag_schema import AatamsSattagQcSchema,get_metadata_from_filename

NRT_FILE_REMOVAL_MSG = "NRT file {file} schedule to {ptype}"
NRT_TIMESTAMP_COMPARISON_MSG = (
    "NRT update requested: Comparing timestamps of metadata file in {0} and {1}"
)
NRT_TIMESTAMP_DIFFERS_MSG = "Incoming file {incoming_file} containing {within_file} contains older entries than current NRT state from {archival_file}"

logger = logging.getLogger(__name__)


def aatams_sattag_qc_dm_dest_path(filepath):
    """Return the full filepath string for Delay files."""
    return os.path.join(AATAMS_SATTAG_QC_DM_BASE, os.path.basename(filepath))


def aatams_sattag_qc_nrt_dest_path(filepath):
    """Return the full filepath string for NRT files."""
    return os.path.join(AATAMS_SATTAG_QC_NRT_BASE, os.path.basename(filepath))


class AatamsSattagHandler(HandlerBase):
    """The class for aatams sattag zip/csv files."""

    @staticmethod
    def get_metadata_file(file_list, campaign=None):
        """Return the metadata.csv PipelineFile object within a PipelineFileCollection
        for a certain campaign."""
        if campaign:
            fname = [
                x for x in file_list if "metadata" in x.name and campaign in x.name
            ]
        else:
            fname = [x for x in file_list if "metadata" in x.name]

        if fname:
            return fname[0]
        return None

    def get_remote_metadata_from_zip(self, remote_pfile):
        """Fetch the metdata.csv file from a RemotePipelineFile zip and wrapping it on a
        PipelineFile."""
        # TODO: remove the first try statement when pipeline
        remote_collection = RemotePipelineFileCollection(remote_pfile)
        try:
            download = self.state_query.download
        except AttributeError:
            download = self.state_query._storage_broker.download

        download(remote_collection, self.temp_dir)
        dest_folder = os.path.join(
            self.temp_dir, os.path.dirname(remote_pfile.dest_path)
        )
        local_zipfile = os.path.join(self.temp_dir, remote_pfile.dest_path)

        extract_zip(local_zipfile, dest_folder)

        local_metadata_file = [
            os.path.join(dest_folder, x)
            for x in os.listdir(dest_folder)
            if "metadata" in x
        ]
        try:
            return PipelineFile(local_metadata_file[0])
        except IndexError:
            return None

    def __init__(self, *args, **kwargs):
        """Initialize the class with schema validation."""
        super(AatamsSattagHandler, self).__init__(*args, **kwargs)
        self.schema = AatamsSattagQcSchema()
        self.validation_call = self.schema.extensive_validation
        self.mode = ''
        self.current_campaign = ''
        # Use below to just validate the file names and csv headers
        # self.validation_call = self.schema.quick_validation

    def is_nrt_update_required(self, old_metadata_file):
        """Check if updates to the dataset/archive are required by inspecting the most
        recent dates between the new state and remote(current) metadata state."""
        new_valid_data = self.schema.metadata
        _, old_valid_data = self.schema.validate_file(old_metadata_file)
        new_recent_date = sorted((x for x in new_valid_data["qc_end_date"] if x))[-1]
        old_recent_date = sorted((x for x in old_valid_data["qc_end_date"] if x))[-1]
        return new_recent_date >= old_recent_date

    def nrt_aware(self):
        """Check if class is initialize for NRT type of files."""
        for regex_string in self.allowed_dest_path_regexes:
            if AATAMS_SATTAG_QC_NRT_BASE not in regex_string:
                return False
        return True

    def schedule_file_removal(self, remote_pipeline_file):
        """schedule a file to be removed."""
        filename = remote_pipeline_file.name
        file_to_remove = PipelineFile(
            filename, is_deletion=True, dest_path=self.dest_path_function(filename),
        )
        file_to_remove.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
        self.file_collection.add(file_to_remove)
        logger.info(
            NRT_FILE_REMOVAL_MSG.format(
                file=file_to_remove, ptype=file_to_remove.publish_type
            )
        )

    def process_nrt(self):
        """Process NRT files, only allowing updates to occur if the new files for
        certain campaigns are more recent."""

        previous_files = self.state_query.query_storage(self.dest_path_function(""))
        if not previous_files:
            return


        try:
            old_zip_file = [x for x in previous_files if self.current_campaign in x.name][0]
        except IndexError:
            return

        old_metadata_file = self.get_remote_metadata_from_zip(old_zip_file)
        if not old_metadata_file:
            return

        new_metadata_file = self.get_metadata_file(
            self.file_collection, self.current_campaign
        )

        logger.info(
            NRT_TIMESTAMP_COMPARISON_MSG.format(
                old_zip_file.dest_path, new_metadata_file.src_path
            )
        )

        if not self.is_nrt_update_required(old_metadata_file.local_path):
            raise InvalidFileContentError(
                NRT_TIMESTAMP_DIFFERS_MSG.format(
                    incoming_file=self.input_file_object.src_path,
                    within_file=new_metadata_file.src_path,
                    archival_file=old_zip_file.dest_path,
                )
            )
        # TODO: Enable below to schedule fil es to be deleted, if required
        # for remote_file in previous_files:
        #     self.schedule_file_removal(remote_file)

    def preprocess(self):
        """Validate the received file(s) and set publish types."""
        try:
            self.mode, self.current_campaign = get_metadata_from_filename(self.input_file_object.name)
        except ValueError as e:
            raise InvalidFileFormatError(''.join(e.args))

        files_in_zip = self.file_collection.get_attribute_list("local_path")
        self.validation_call(files_in_zip)

        self.input_file_object.publish_type = (
            PipelineFilePublishType.HARVEST_ARCHIVE_UPLOAD
        )
        zip_filename = os.path.basename(self.input_file_object.src_path)
        self.input_file_object.dest_path = self.dest_path_function(zip_filename)

        self.file_collection.add(self.input_file_object)
        self.file_collection.filter_by_attribute_value(
            "file_type", FileType.CSV,
        ).set_publish_types(PipelineFilePublishType.HARVEST_ONLY)

    def process(self):
        """Process NRT files if this class is initialize as NRT pipeline."""
        if self.mode == 'nrt' and self.nrt_aware():
            self.process_nrt()


# AATAMS DM destination path
AATAMS_SATTAG_QC_DM_BASE = "IMOS/AATAMS/satellite_tagging/ATF_Location_QC_DM"
AATAMS_SATTAG_QC_DM_OPTS = {
    "allowed_extensions": [".zip", ".csv"],
    "allowed_regexes": ["^.+_dm\\.(zip|csv)$"],
    "allowed_archive_path_regexes": ['^' + AATAMS_SATTAG_QC_DM_BASE + ".+\\.zip$"],
    "allowed_dest_path_regexes": ['^' + AATAMS_SATTAG_QC_DM_BASE],
    "archive_input_file": True,
    "dest_path_function": aatams_sattag_qc_dm_dest_path,
    "archive_path_function": aatams_sattag_qc_dm_dest_path,
}
AatamsSattagQcDmHandler = partial(AatamsSattagHandler, **AATAMS_SATTAG_QC_DM_OPTS)

# AATAMS NRT destination path
AATAMS_SATTAG_QC_NRT_BASE = "IMOS/AATAMS/satellite_tagging/ATF_Location_QC_NRT"
AATAMS_SATTAG_QC_NRT_OPTS = {
    "allowed_extensions": [".zip", ".csv"],
    "allowed_regexes": ["^.+_nrt\\.(zip|csv)$"],
    "allowed_archive_path_regexes": ['^' + AATAMS_SATTAG_QC_NRT_BASE + ".+\\.zip$"],
    "allowed_dest_path_regexes": ['^' + AATAMS_SATTAG_QC_NRT_BASE],
    "archive_input_file": True,
    "dest_path_function": aatams_sattag_qc_nrt_dest_path,
    "archive_path_function": aatams_sattag_qc_nrt_dest_path,
}
AatamsSattagQcNrtHandler = partial(AatamsSattagHandler, **AATAMS_SATTAG_QC_NRT_OPTS)
