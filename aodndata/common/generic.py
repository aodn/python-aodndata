from aodncore.pipeline import HandlerBase, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidInputFileError


class GenericHandler(HandlerBase):
    """This is a generic handler that implements the simple validate-publish workflow for a single netCDf file or a
    collection of netCDF files. A dest_path_function argument must be specified. The entire process fails if any
    input file is ecluded by the regex patterns, is not a valid netCDF file, or fails the compliance checks.

    Usage:
    handler = GenericHandler(input_file,
                             include_regexes=['*\.nc'],
                             exclude_regexes=[],
                             check_params={'checks': ['cf', 'imos:1.4']},
                             dest_path_function=my_dest_path
                             )
    handler.run()
    """

    def __init__(self, *args, **kwargs):
        super(GenericHandler, self).__init__(*args, **kwargs)

    @staticmethod
    def dest_path(filename):
        raise NotImplementedError('dest_path_function not specified!')

    def preprocess(self):
        """Check that every input file is valid according to the include/exclude regex patterns. Any non-matching
        file will be marked as NO_ACTION after the _resolve step.

        :return: None
        """
        self.logger.info("Running preprocess from child class")

        invalid_files = [f.name for f in self.file_collection
                         if f.publish_type == PipelineFilePublishType.NO_ACTION]
        if invalid_files:
            raise InvalidInputFileError(
                "File name(s) don't match the pattern expected for this run location: {name}".format(
                    name=str(invalid_files)
                )
            )
