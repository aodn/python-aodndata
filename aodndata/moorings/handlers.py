import re

from netCDF4 import Dataset

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError

from aodndata.moorings.classifiers import MooringsFileClassifier, DwmFileClassifier
from aodndata.moorings.burst_average import create_burst_average_netcdf


class MooringsHandler(HandlerBase):
    """Handler for data from the IMOS moorings facilities (DWM, ANMN). It handles the following file types:
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

        If there are any netCDF files from burst-sampling instruments in the collection, create the burst-averaged
        version of each and add them to the collection.

        :return: None
        """
        self.logger.info("Checking for invalid files and adjusting check/publish properties.")

        invalid_files = self.file_collection.filter_by_attribute_id('publish_type', PipelineFilePublishType.UNSET)
        if invalid_files:
            raise InvalidFileNameError(
                "File name(s) don't match the pattern expected for this upload location: {names}".format(
                    names=invalid_files.get_attribute_list('name')
                )
            )

        # Burst-processing for FV01 files with burst-sampling global attributes
        burst_files = (self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
                                           .filter_by_attribute_regex('name', r'.*_FV01_')
                       )
        for f in burst_files:
            with Dataset(f.src_path, mode='r') as D:
                has_interval = hasattr(D, 'instrument_burst_interval')
                has_duration = hasattr(D, 'instrument_burst_duration')
                is_adcp = ('DIST_ALONG_BEAMS' in D.dimensions or 'HEIGHT_ABOVE_SENSOR' in D.dimensions)
            if not (has_interval and has_duration) or is_adcp:
                continue

            self.logger.info("Burst-processing {f.name}".format(f=f))
            product_path = create_burst_average_netcdf(f.src_path, self.products_dir)
            product_file = PipelineFile(product_path, file_update_callback=self._file_update_callback)
            product_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(product_file)

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


class DwmHandler(MooringsHandler):
    """Handler for DWM files.

    It does mostly the same as MooringsHandler, but there are a few DWM-specific tweaks, and the dest_path
    method is different.
    """

    def __init__(self, *args, **kwargs):
        super(DwmHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.zip']

    def process(self):
        """Handle a zip file containing images and no NetCDF files or a zip file containing calibration files and no NetCDF files. In this case we just want to publish the zip file
        itself, not the individual images, and the same for the calibration zip files. If we encounter a "mixed" zip file with images/calibration files and netCDF files,
        we're just going to give up, for now.
        """        
        images = PipelineFileCollection(f for f in self.file_collection if f.file_type.is_image_type)
        netcdfs = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        is_zip = self.file_type is FileType.ZIP
        have_images = len(images) > 0
        have_netcdfs = len(netcdfs) > 0
        is_image_zip_pattern = have_images and DwmFileClassifier.SOTS_IMAGES_ZIP_PATTERN.match(self.file_basename) is not None
        is_calibration_zip_pattern = DwmFileClassifier.SOTS_CALIBRATION_ZIP_PATTERN.match(self.file_basename) is not None
        if is_image_zip_pattern:
            zip_file_msg = 'images'
        elif is_calibration_zip_pattern:
            zip_file_msg = 'calibration'
        else:
            zip_file_msg = 'no image or calibration file'

        if have_netcdfs:
            non_netcdfs = self.file_collection.filter_by_attribute_id_not('file_type', FileType.NETCDF)
            have_non_netcdfs = len(non_netcdfs) > 0
            if have_non_netcdfs:
                raise InvalidFileContentError(
                    "Zip file contains both netCDFs and other file types. Don't know what to do!"
                    " They are handled differently, so please upload only one at a time."
                    )
        elif is_image_zip_pattern or is_calibration_zip_pattern:
            self.logger.info("Zip file contains {} and no netCDF files. "
                             "Publishing original zip file instead of its contents.".format(zip_file_msg))
            self.file_collection.set_publish_types(PipelineFilePublishType.NO_ACTION)
            self.input_file_object.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(self.input_file_object)
        else:
            raise InvalidFileNameError("file {} has not the right pattern for an image or calibration zip file".format(self.file_basename))

    dest_path = DwmFileClassifier.dest_path