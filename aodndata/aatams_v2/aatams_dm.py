import os

from aodncore.pipeline import FileType, HandlerBase, PipelineFilePublishType
from aodncore.util.fileops import extract_zip

from aatams_dm_schema import AATAMS_DM_Schema

# AATAMS DM global constants
AATAMS_SATTAG_DM_BASE = "IMOS/AATAMS/AATAMS_SATTAG_DM"  # TODO


class NEWHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(NEWHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.zip']
        # self.dest_path_function =
        # self.archive_path_function =
        # self.include_regexes =
        # self.allowed_archive_path_regexes=None,
        # self.allowed_dest_path_regexes=None,
        # self.allowed_extensions=None,
        # self.allowed_regexes=None,
        # self.archive_input_file=False,
        # self.archive_path_function=None,
        # self.celery_task=None,
        # self.check_params=None,
        # self.config=None,
        # self.custom_params=None,
        # self.dest_path_function=None,
        # self.error_cleanup_regexes=None,
        # self.exclude_regexes=None,
        # self.harvest_params=None,
        # self.harvest_type='talend',
        # self.include_regexes=None,
        # self.notify_params=None,
        # self.upload_path=None,
        # self.resolve_params=None

        self.SCHEMA = AATAMS_DM_Schema()
        self.validation_call = self.SCHEMA.extensive_validation
        # self.validation_call = self.SCHEMA.quick_validation

    def preprocess(self):
        if self.file_type is FileType.ZIP:
            path = self.temp_dir
            extract_zip(self.file_collection[0].local_path, path)
            files_in_zip = [os.path.join(path, x) for x in os.listdir(path)]

            if self.validation_call(files_in_zip):
                self.file_collection.add(files_in_zip)

            self.file_collection.\
                filter_by_attribute_id('file_type', FileType.ZIP).\
                set_publish_types(PipelineFilePublishType.ARCHIVE_ONLY)

            self.file_collection.\
                filter_by_attribute_value('extension', '.csv').\
                set_publish_types(PipelineFilePublishType.HARVEST_ONLY)

    def dest_path(self, filepath):
        return os.path.join(AATAMS_SATTAG_DM_BASE, os.path.basename(filepath))

    def archive_path(self, filepath):
        return self.dest_path(filepath)
