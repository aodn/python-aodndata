import os
from os import listdir
from os.path import isfile, join

from aodncore.pipeline import FileType, HandlerBase, PipelineFilePublishType
from aodncore.util.fileops import extract_zip

AATAMS_SATTAG_DM_BASE = "IMOS/AATAMS/AATAMS_SATTAG_DM"


class AatamsDmHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(AatamsDmHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.mdb', '.zip', '.manifest']

    def preprocess(self):

        """ if input file is ZIP we add it to the collection """
        if self.file_type is FileType.ZIP:
            self.file_collection.add(self.input_file)

        """ if input file is manifest (containing zips), zip is already added to the collection.
         we extract the mdb and add them to the collection
        """
        if self.file_type is FileType.SIMPLE_MANIFEST:
            extract_zip(self.file_collection[0].local_path, self.temp_dir)
            mdb_path = [os.path.join(self.temp_dir, f)
                        for f in listdir(self.temp_dir)
                        if isfile(join(self.temp_dir, f))
                        and f.endswith('.mdb')][0]

            self.file_collection.add(mdb_path)

        """ setting the default publish type of both zip and mdb files"""
        self.file_collection.filter_by_attribute_id('file_type', FileType.ZIP). \
             set_publish_types(PipelineFilePublishType.ARCHIVE_ONLY)

        self.file_collection.filter_by_attribute_value('extension', '.mdb').\
            set_publish_types(PipelineFilePublishType.HARVEST_ONLY)

    def dest_path(self, filepath):
        return os.path.join(AATAMS_SATTAG_DM_BASE, os.path.basename(filepath))

    def archive_path(self, filepath):
        return self.dest_path(filepath)
