from datetime import datetime, timezone
import os

from aodncore.pipeline import HandlerBase, FileType, PipelineFileCheckType, PipelineFilePublishType


class ImosBgcDbHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(ImosBgcDbHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.zip', '.csv']
        self.include_regexes = [".*\\.csv$"]
        self.harvest_type = 'csv'
        self.archive_input_file = True
        self.input_file_archive_path = self.archive_path(self.input_file)

    def preprocess(self):
        """
        Set up CSV files to be checked against TableSchema, harvested, and saved to S3.
        """
        csv_files = self.file_collection.filter_by_attribute_id('file_type', FileType.CSV)
        csv_files.set_check_types(PipelineFileCheckType.TABLE_SCHEMA_CHECK)
        csv_files.set_publish_types(PipelineFilePublishType.HARVEST_UPLOAD)

    def dest_path(self, filepath):
        """Destination path function for CSV files."""
        return os.path.join('IMOS', 'BGC_DB', os.path.basename(filepath))

    def archive_path(self, filepath):
        """Archive path for original input file."""
        dest_path = self.dest_path(filepath)
        timestamp = datetime.now(timezone.utc).strftime('.%Y%m%dT%H%M%SZ')
        basename, ext = os.path.splitext(dest_path)
        return basename + timestamp + ext
