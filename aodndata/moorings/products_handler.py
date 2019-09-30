import json

from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLike, PropertyIsNotEqualTo, And

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodncore.pipeline.files import RemotePipelineFileCollection
from aodncore.util.wfs import ogc_filter_to_string

from aodntools.timeseries_products.aggregated_timeseries import main_aggregator

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
        self.allowed_extensions = ['.json_manifest']
        self.product_site_code = None
        self.product_variables = None

    def preprocess(self):
        """Collect available input files and create the products, adding them to the collection to be published."""

        # Read the manifest file and extract key parameters for product
        with open(self.input_file) as f:
            manifest = json.load(f)
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
        # TODO: find out why this calls getCapabilities twice (and takes 40s even when response mocked with httpretty)
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
        input_list = input_file_collection.get_attribute_list('local_path')

        # TODO: Run compliance checks and remove non-compliant files from the input list (log them).

        # For each variable, generate product and add to file_collection.
        for var in self.product_variables:
            self.logger.info("Generating aggregated timeseries product for {var}".format(var=var))

            # TODO: Need to filter input_list to the files relevant for this var (use results of WFS query?)
            product_url, errors = main_aggregator(input_list, var, self.product_site_code, base_path=self.products_dir)
            if errors:
                self.logger.warn(
                    "Files were excluded from the aggregation: {error_files}".format(error_files=list(errors))
                )
            product_file = PipelineFile(product_url, file_update_callback=self._file_update_callback)
            product_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(product_file)

    dest_path = MooringsProductClassifier.dest_path

