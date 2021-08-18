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
        self.input_file_archive_path = self.dest_path(self.input_file)

    def preprocess(self):
        """
        Set up CSV files to be checked against TableSchema and harvested.
        They don't need to be uploaded as the entire zip (input_file) will be archived.
        """
        csv_files = self.file_collection.filter_by_attribute_id('file_type', FileType.CSV)
        csv_files.set_check_types(PipelineFileCheckType.TABLE_SCHEMA_CHECK)
        csv_files.set_publish_types(PipelineFilePublishType.HARVEST_ONLY)

    def dest_path(self, filepath):
        """
        Destination/archive path function.
        """
        base_path = "IMOS/BGC_DB"
        timestamp = datetime.now(timezone.utc).strftime('.%Y%m%dT%H%M%SZ')
        basename, ext = os.path.splitext(os.path.basename(filepath))
        dest_path = os.path.join(base_path, basename + timestamp + ext)
        return dest_path
