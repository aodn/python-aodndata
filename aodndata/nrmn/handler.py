#!/usr/bin/env python
import os

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
# from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError


class NrmnHandler(HandlerBase):
    """Handler for NRMN .csv files in .zip file.

    It handles the .zip file with .csv files that have the name pattern 'ep_...'.
    """

    def __init__(self, *args, **kwargs):
        super(NrmnHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.zip', '.csv']

    def process(self):
        """Handle a zip file containing .csv files. In this case we just want to publish the .zip file
        itself, not the individual .csv files.
        """

        self.file_collection.set_publish_types(PipelineFilePublishType.HARVEST_ONLY)

    def dest_path(self, filepath):
        """
        Destination object path for the NRMN .zip file or the individual .csv files.
        """

        base_path = "IMOS/NRMN"
        dest_path = os.path.join(base_path, os.path.basename(filepath))
        return dest_path

    # dest_path = NrmnHandler.dest_path
