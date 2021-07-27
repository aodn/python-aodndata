import os

from aodncore.pipeline import HandlerBase, FileType, PipelineFileCheckType


class ImosBgcDbHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(ImosBgcDbHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.zip', '.csv']
        self.include_regexes = [".*\\.csv$"]
        self.harvest_type = 'csv'

    def preprocess(self):
        """Set the check type to TableSchema check for all CSV files."""
        self.file_collection \
            .filter_by_attribute_id('file_type', FileType.CSV) \
            .set_check_types(PipelineFileCheckType.TABLE_SCHEMA_CHECK)

    def dest_path(self, filepath):
        """
        Destination object path for the BGC test .zip file or the individual .csv files.
        """

        base_path = "IMOS/BGC"
        dest_path = os.path.join(base_path, os.path.basename(filepath))
        return dest_path
