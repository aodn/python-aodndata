from aodncore.pipeline import HandlerBase, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError


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
        file will be left with publish_type UNSET after the _resolve step.

        :return: None
        """
        self.logger.info("Checking for invalid files.")

        invalid_files = self.file_collection.filter_by_attribute_id('publish_type', PipelineFilePublishType.UNSET)
        if invalid_files:
            raise InvalidFileNameError(
                "File name(s) don't match the pattern expected for this upload location: {names}".format(
                    names=map(str, invalid_files.get_attribute_list('name'))
                )
            )
