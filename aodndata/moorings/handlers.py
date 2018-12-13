import re

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection
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

    def postprocess(self):
        """Set error_cleanup_regexes so that if the same file was uploaded previously and failed, it can now be
        removed from the error directory (by setting "success_exit_policies" in the pipeline config to
        "DELETE_CUSTOM_REGEXES_FROM_ERROR_STORE").
        """

        # remove creation date from file name, as this can change when the same file is re-processed
        base = re.sub(r"_C-[0-9]{8}.*", r"_C-", self.file_basename)
        cleanup_regexes = ["{base}{wildcard}".format(base=re.escape(base), wildcard=r".*\.[0-9a-f\-]{36}")]
        self.error_cleanup_regexes = cleanup_regexes
        self.logger.info("error_cleanup_regexes set to {}".format(cleanup_regexes))

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
        """Handle a zip file containing images and no NetCDF files. In this case we just want to publish the zip file
        itself, not the individual images. If we encounter a "mixed" zip file with images and netCDF files,
        we're just going to give up, for now.
        """
        images = PipelineFileCollection(f for f in self.file_collection if f.file_type.is_image_type)
        netcdfs = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        is_zip = self.file_type is FileType.ZIP
        have_images = len(images) > 0
        have_netcdfs = len(netcdfs) > 0
        if is_zip and have_images:
            if have_netcdfs:
                raise InvalidFileContentError(
                    "Zip file contains both images and netCDFs. Don't know what to do!"
                    " They are handled differently, so please upload only one at a time."
                )
            if not AbosFileClassifier.SAZ_IMAGES_ZIP_PATTERN.match(self.file_basename):
                raise InvalidFileNameError(
                    "Zip file contains images, but its name does not match pattern for images zip file"
                )

            self.logger.info("Zip file contains images and no netCDF files. "
                             "Publishing original zip file instead of its contents.")

            self.file_collection.set_publish_types(PipelineFilePublishType.NO_ACTION)
            self.input_file_object.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(self.input_file_object)

    dest_path = AbosFileClassifier.dest_path
