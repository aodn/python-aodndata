"""Animal Tracking ACOUSTIC handler"""
import os
import pandas as pd
import re

from aodncore.pipeline import (
    HandlerBase,
    PipelineFilePublishType,
    PipelineFileCheckType,
    )

from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidInputFileError
from aodncore.util.misc import get_pattern_subgroups_from_string

from aodndata.aatams.aatams_acoustic_index_tmp import extract_metadata, create_empty_dataframe

FILE_TYPE_NEED_INDEX = ('QC', 'QC_daily_summary')
AT_ACOUSTIC_FILE_PATTERN = re.compile(r"""
                                      ^IMOS_ATF-ACOUSTIC_TAGID_
                                      (?P<transmitter_id>A(69|180)-[0-9]{4}-[0-9]{1,5})_
                                      (?P<release_id>[0-9]{1,10}_[0-9]{1,10})
                                      (?P<product_type>.*)
                                      \.csv$""", re.VERBOSE)


def get_type(filepath):
    """return at_acoustic_file_type, the file type of an AT_ACOUSTIC file based on its filename"""
    # TODO: currently not in used, we'll need it when we receive the daily product of the QC'd detections
    #  check a working example: acron handler
    file_basename = os.path.basename(filepath)
    unknown_product = False
    if AT_ACOUSTIC_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, AT_ACOUSTIC_FILE_PATTERN)
        product_type = fields['product_type']

        if product_type == '_QC_daily_summary':
            at_acoustic_file_type = "QC_daily_summary"

        elif product_type is None:
            at_acoustic_file_type = "QC"

        else:
            unknown_product = True
    else:
        unknown_product = True

    if unknown_product:
        raise InvalidFileNameError("file name: \"{filename}\" Unknown QC product type from filename".
                                   format(filename=file_basename))

    return at_acoustic_file_type


class AnimalTrackingAcousticHandler(HandlerBase):
    """The class for AnimalTracking acoustic qc
     zip/csv files."""
    def __init__(self, *args, **kwargs):
        super(AnimalTrackingAcousticHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.zip', '.csv']
        self.include_regexes = AT_ACOUSTIC_FILE_PATTERN
        #["^IMOS_ATF-ACOUSTIC_TAGID_.*\.csv$"]
        self.check_params = {"tableschema_filename_pattern": "^IMOS_ATF-ACOUSTIC"}
        self.harvest_type = 'csv'

    def preprocess(self):

        """Check that every input file is valid according to the include/exclude regex patterns. Any non-matching
        file will be left with publish_type UNSET after the _resolve step.

        Set up CSV files to be checked against TableSchema and set publish types.

        :return: None
        """

        self.logger.info("Checking for invalid files and adjusting check/publish properties.")

        #  stop if doesn't match expected regex
        invalid_files = self.file_collection.filter_by_attribute_id('publish_type', PipelineFilePublishType.UNSET)
        if invalid_files:
            raise InvalidFileNameError(
                "File name(s) don't match the pattern expected for this upload location: {names}. Expected pattern "
                "is IMOS_ATF-ACOUSTIC_TAGID_transmitterID_tagID_transmitterdeploymentID.csv"
                .format(names=invalid_files.get_attribute_list('name')
                        )
            )
        if len(self.file_collection) == 0:
            raise InvalidInputFileError("no csv file to index in '{zip}'".format(zip=os.path.basename(self.input_file)))

        # validate schema on the received csv files
        self.file_collection.set_check_types(PipelineFileCheckType.TABLE_SCHEMA_CHECK)
        # upload to S3 only
        self.file_collection.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

    def process(self):
        """
        create a temporary pandas dataframe extracting the file metadata to ingest into the database,
        the dataframe is then turned into a csv (index_tmp.csv) harvested by the csv harvester
        """

        self.logger.info("Creating index_tmp.csv, indexing csv files and extracting data and file URL from {n} input "
                         "files".format(n=len(self.file_collection)))

        tag_files_list = self.file_collection  #.filter_by_attribute_regex('name', r'^IMOS_ATF-ACOUSTIC_TAGID_.*\.csv$')
        index_tmp_file_path = os.path.join(self.temp_dir, 'index_tmp.csv')
        df_index_tmp = create_empty_dataframe()
        for tag_file in tag_files_list:
            destination_s3 = self.dest_path(tag_file.name)
            self.logger.info("Indexing the file")
            df_csv_extract = extract_metadata(tag_file, destination_s3)
            df_index_tmp = pd.concat([df_index_tmp, df_csv_extract])
        df_index_tmp.to_csv(index_tmp_file_path, index=False)

        self.logger.info("adding index_tmp.csv to collection")
        self.file_collection.add(index_tmp_file_path, publish_type=PipelineFilePublishType.HARVEST_ONLY)
        self.logger.info("index_tmp added to collection and being harvested")

    @staticmethod
    def dest_path(filepath):
        """Destination path function for CSV files."""
        return os.path.join('IMOS', 'AATAMS', 'acoustic_detections_QC', os.path.basename(filepath))
