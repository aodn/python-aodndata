import json

from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLike, PropertyIsNotEqualTo, And

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodncore.pipeline.files import RemotePipelineFileCollection
from aodncore.util.wfs import ogc_filter_to_string

from aodndata.moorings.classifiers import MooringsFileClassifier


class MooringsProductClassifier(MooringsFileClassifier):
    @classmethod
    def _get_data_category(cls, input_file):
        return 'aggregated_timeseries'

    @classmethod
    def _get_product_level(cls, input_file):
        return ''


class MooringsProductsHandler(HandlerBase):
    """Handler to create products from moorings files.

    The input file is a JSON document containing a site_code and a list of variables. The handler will then create
    the products for each variable at that site, using all the relevant input files available on S3.

    The structure of the JSON document will be something like this:
    {
        "site_code": "NRSMAI",
        "variables": ["TEMP", "PSAL", "DOX1", "DOX2", "CPHL"]
    }
    """

    FILE_INDEX_LAYER = 'imos:moorings_all_map'

    def __init__(self, *args, **kwargs):
        super(MooringsProductsHandler, self).__init__(*args, **kwargs)
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.json']
        self.product_site_code = None
        self.product_variables = None

    def preprocess(self):
        """Collect available input files and create the products, adding them to the collection to be published."""

        # Don't want to publish the manifest file, so remove it from the collection
        self.file_collection.pop()

        # Read the manifest file and extract key parameters for product
        with open(self.input_file) as f:
            try:
                manifest = json.load(f)
            except ValueError as e:
                raise InvalidFileContentError("invalid JSON file '{self.input_file}' ({e})".format(self=self, e=e))

        try:
            self.product_site_code = manifest['site_code']
            self.product_variables = manifest['variables']
        except KeyError:
            raise InvalidFileContentError(
                "manifest file '{self.input_file}' missing information (site_code, variables)".format(self=self)
            )
        self.logger.info(
            "Creating products for site {self.product_site_code}, variables {self.product_variables}".format(self=self)
        )

        # Find out what relevant input files are available on S3 for this site.
        filter_list = [PropertyIsEqualTo(propertyname='site_code', literal=self.product_site_code),
                       PropertyIsEqualTo(propertyname='file_version', literal='1'),
                       PropertyIsEqualTo(propertyname='realtime', literal='false'),
                       PropertyIsNotEqualTo(propertyname='data_category', literal='Biogeochem_profiles'),
                       PropertyIsNotEqualTo(propertyname='data_category', literal='CTD_profiles')
                       ]
        ogc_filter = ogc_filter_to_string(And(filter_list))

        # Note I need to access _wfs_broker to be able to use query_urls_for_layer() with a filter,
        # as the corresponding StateQuery method doesn't accept additional kwargs.
        # TODO: replace ._wfs_broker.query_urls_for_layer() with .query_wfs_urls_for_layer() once aodncore has been updated
        input_files = self.state_query._wfs_broker.query_urls_for_layer(self.FILE_INDEX_LAYER,
                                                                        ogc_filter=ogc_filter,
                                                                        url_property_name='url'
                                                                        )
        self.logger.info("Downloading {n} input files".format(n=len(input_files)))

        # Download input files to local cache.
        input_file_collection = RemotePipelineFileCollection(input_files)
        input_file_collection.download(self._upload_store_runner.broker, self.temp_dir)
        # TODO: Replace temp_dir above with cache_dir?

        # TODO: Run compliance checks and remove non-compliant files from the input list (log them).

        # TODO: For each variable, generate product and add to file_collection.
        # Call product code from aodntools package

    dest_path = MooringsProductClassifier.dest_path

