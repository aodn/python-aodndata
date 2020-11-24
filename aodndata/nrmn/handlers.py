#!/usr/bin/env python
import os
import re

from netCDF4 import Dataset

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError

from aodndata.moorings.classifiers import MooringsFileClassifier, AbosFileClassifier, DwmFileClassifier
from aodndata.moorings.burst_average import create_burst_average_netcdf


class NrmnHandler(HandlerBase):
    """Handler for NRMN csv files.

    It does mostly the same as MooringsHandler, but there are a few DWM-specific tweaks, and the dest_path
    method is different.
    """

    def __init__(self, *args, **kwargs):
        super(NrmnHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.zip']

    def process(self):
        """Handle a zip file containing csv files. In this case we just want to publish the zip file
        itself, not the individual images. If we encounter a "mixed" zip file with images and netCDF files,
        we're just going to give up, for now.
        """
        # images = PipelineFileCollection(f for f in self.file_collection if f.file_type.is_image_type)
        # netcdfs = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        __import__('pdb').set_trace()
        self.file_collection.set_publish_types(PipelineFilePublishType.HARVEST_ONLY)
        csvs = PipelineFileCollection(f for f in self.file_collection if f.file_type.is_csv_type)
        is_zip = self.file_type is FileType.ZIP
        # have_images = len(images) > 0
        # have_netcdfs = len(netcdfs) > 0
        have_csvs = len(csvs) > 0
        if is_zip and have_images:
            if have_netcdfs:
                raise InvalidFileContentError(
                    "Zip file contains both images and netCDFs. Don't know what to do!"
                    " They are handled differently, so please upload only one at a time."
                )

            self.logger.info("Zip file contains csv files. Publishing original zip file instead of its contents.")

            self.file_collection.set_publish_types(PipelineFilePublishType.NO_ACTION)
            self.input_file_object.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(self.input_file_object)


    def dest_path(self, filepath):
        """
        Destination object path for a moorings netCDF file. Of the form:
        """
        dest_path = os.path.join(self.upload_destination, os.path.basename(filepath))
        return dest_path


dest_path = NrmnHandler.dest_path