from aodncore.pipeline import HandlerBase, PipelineFilePublishType, PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodndata.moorings.classifiers import MooringsFileClassifier


class MooringsHandler(HandlerBase):
    """Handler for data from the IMOS moorings facilities (ABOS, ANMN). It handles the following file types:
     * NetCDf (timeseries or profile);
     * PDF (field logsheet);
     * PNG (plots);
     * CNV (text version of CTD profiles);
     * a collection of the above types

    The entire process fails if any input file is excluded by the regex patterns, or is a netCDF file that fails the
    compliance checks.

    Usage:
    handler = MooringsHandler(input_file,
                             include_regexes=['*\.nc'],
                             check_params={'checks': ['cf', 'imos:1.4']},
                             )
    handler.run()
    """

    def __init__(self, *args, **kwargs):
        super(MooringsHandler, self).__init__(*args, **kwargs)
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.nc', '.pdf', '.png', '.cnv', '.zip']

    def preprocess(self):
        """Check that every input file is valid according to the include/exclude regex patterns. Any non-matching
        file will be marked as NO_ACTION after the _resolve step.

        Also adjust the check_type and publish_type properties for non-NetCDF files. These are currently not checked
        or harvested, but they need to be uploaded to S3.

        :return: None
        """
        self.logger.info("Checking for invalid files and adjusting check/publish properties.")

        invalid_files = []
        for f in self.file_collection:
            if f.publish_type == PipelineFilePublishType.NO_ACTION:
                invalid_files.append(f.name)
            if f.extension != '.nc':
                f.check_type = PipelineFileCheckType.NO_ACTION
                f.publish_type = PipelineFilePublishType.UPLOAD_ONLY

        if invalid_files:
            raise InvalidFileNameError(
                "File name(s) don't match the pattern expected for this run location: {name}".format(
                    name=str(invalid_files)
                )
            )

    dest_path = MooringsFileClassifier.dest_path