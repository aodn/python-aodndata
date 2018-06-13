from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, FileType
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodndata.moorings.classifiers import MooringsFileClassifier, AbosFileClassifier


class MooringsHandler(HandlerBase):
    """Handler for data from the IMOS moorings facilities (ABOS, ANMN). It handles the following file types:
     * NetCDf (timeseries or profile);
     * PDF (field logsheet);
     * PNG (plots);
     * CNV (text version of CTD profiles);
     * a collection of the above types

    The entire process fails if any input file is excluded by the regex patterns, or is a netCDF file that fails the
    compliance checks.
    """

    def __init__(self, *args, **kwargs):
        super(MooringsHandler, self).__init__(*args, **kwargs)
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.nc', '.pdf', '.png', '.cnv', '.zip']

    def preprocess(self):
        """Check that every input file is valid according to the include/exclude regex patterns. Any non-matching
        file will be left with publish_type UNSET after the _resolve step.

        Also adjust the check_type and publish_type properties for non-NetCDF files. These are currently not checked
        or harvested, but they need to be uploaded to S3.

        :return: None
        """
        self.logger.info("Checking for invalid files and adjusting check/publish properties.")

        invalid_files = self.file_collection.filter_by_attribute_id('publish_type', PipelineFilePublishType.UNSET)
        if invalid_files:
            raise InvalidFileNameError(
                "File name(s) don't match the pattern expected for this upload location: {names}".format(
                    names=map(str, invalid_files.get_attribute_list('name'))
                )
            )

        non_nc_files = self.file_collection.filter_by_attribute_id_not('file_type', FileType.NETCDF)
        non_nc_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

    dest_path = MooringsFileClassifier.dest_path


class AbosHandler(MooringsHandler):
    """Handler for ABOS files.

    It does mostly the same as MooringsHandler, but there are a few ABOS-specific tweaks, and the dest_path
    method is different.
    """

    def __init__(self, *args, **kwargs):
        super(AbosHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.zip']

    def process(self):
        """Handle a zip file containing *only* jpg images. In this case we just want to publish the zip file itself,
        not the individual images. If we encounter a "mixed" zip file with images and netCDF files, we're just going
        to give up, for now.
        """
        images = self.file_collection.filter_by_attribute_id('file_type', FileType.JPEG)
        is_zip = self.file_type is FileType.ZIP
        have_images = len(images) > 0
        only_images = images == self.file_collection
        if is_zip and have_images:
            if not only_images:
                raise InvalidFileContentError(
                    "Zip file contains both images and netCDFs. Don't know what to do!"
                    " They are handled differently, so please upload only one at a time."
                )

            self.logger.info("Zip file contains only images. Publishing original zip file instead of images.")

            images.set_publish_types(PipelineFilePublishType.NO_ACTION)
            self.input_file_object.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            self.file_collection.add(self.input_file_object)

    dest_path = AbosFileClassifier.dest_path
