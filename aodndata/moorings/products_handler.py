from collections import defaultdict
import json

from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLike, PropertyIsNotEqualTo, And

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import ComplianceCheckFailedError, InvalidFileContentError, InvalidFileNameError
from aodncore.pipeline.files import RemotePipelineFileCollection, RemotePipelineFile
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
        self.input_file_collection = None
        self.input_file_variables = None
        self.excluded_files = defaultdict(set)

    def _read_manifest(self):
        """Read the manifest file and extract key parameters for product"""
        with open(self.input_file) as f:
            manifest = json.load(f)

        try:
            self.product_site_code = manifest['site_code']
            self.product_variables = manifest['variables']
        except KeyError:
            raise InvalidFileContentError(
                "manifest file '{self.input_file}' missing information (site_code, variables)".format(self=self)
            )

    def _get_input_files(self):
        """Download input files to local cache.

        Based on the product_site_code and product_variables attributes, query geoserver to find all public files
        relevant to the product, download them to the handler's temporary directory. Set the handler's
        input_file_variables attributes to a dict mapping file dest_path to a list of variables in the file.
        """

        filter_list = [PropertyIsEqualTo(propertyname='site_code', literal=self.product_site_code),
                       PropertyIsEqualTo(propertyname='file_version', literal='1'),
                       PropertyIsEqualTo(propertyname='realtime', literal='false'),
                       PropertyIsNotEqualTo(propertyname='data_category', literal='Biogeochem_profiles'),
                       PropertyIsNotEqualTo(propertyname='data_category', literal='CTD_profiles'),
                       PropertyIsNotEqualTo(propertyname='data_category', literal='aggregated_timeseries')
                       ]
        ogc_filter = ogc_filter_to_string(And(filter_list))
        # Note I need to access _wfs_broker to be able to use query_urls_for_layer() with a filter,
        # as the corresponding StateQuery method doesn't accept additional kwargs.
        # TODO: find out why this calls getCapabilities twice (and takes 40s even when response mocked with httpretty)
        # TODO: replace ._wfs_broker.getfeature_dict() with .getfeature_dict() once aodncore has been updated
        wfs_response = self.state_query._wfs_broker.getfeature_dict(typename=[self.FILE_INDEX_LAYER],
                                                                    filter=ogc_filter,
                                                                    propertyname=['url', 'variables']
                                                                    )
        self.input_file_variables = {f['properties']['url']: f['properties']['variables'].split(', ')
                                     for f in wfs_response['features']
                                     }
        self.input_file_collection = RemotePipelineFileCollection(self.input_file_variables.keys())
        # Download input files to local cache.
        self.logger.info("Downloading {n} input files".format(n=len(self.input_file_collection)))
        self.input_file_collection.download(self._upload_store_runner.broker, self.temp_dir)
        # TODO: Replace temp_dir above with cache_dir?

    def _make_aggregated_timeseries(self):
        """For each variable, generate product and add to file_collection."""

        for var in self.product_variables:
            # Filter input_list to the files relevant for this var
            input_list = [f for f, f_vars in self.input_file_variables.items()
                          if var in f_vars
                          ]
            if not input_list:
                raise InvalidFileContentError("No files to aggregate for {var}".format(var=var))
            self.logger.info("Aggregating {var} ({n} files)".format(var=var, n=len(input_list)))

            product_url, errors = main_aggregator(input_list, var, self.product_site_code, input_dir=self.temp_dir,
                                                  output_dir=self.products_dir,
                                                  download_url_prefix="https://s3-ap-southeast-2.amazonaws.com/imos-data/",
                                                  opendap_url_prefix="http://thredds.aodn.org.au/thredds/dodsC/"
                                                  )
            if errors:
                self.logger.warning("{n} files were excluded from the aggregation.".format(n=len(errors)))
                for f, e in errors.items():
                    self.excluded_files[f].update(e)

            product_file = PipelineFile(product_url, file_update_callback=self._file_update_callback)
            product_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(product_file)

    def preprocess(self):
        """Collect available input files and create the products, adding them to the collection to be published."""

        self._read_manifest()
        self.logger.info(
            "Creating products for site {self.product_site_code}, variables {self.product_variables}".format(self=self)
        )

        self._get_input_files()

        # TODO: Run compliance checks and remove non-compliant files from the input list (log them).

        self._make_aggregated_timeseries()

        # TODO: Include the list of excluded files as another table in the notification email (instead of the log)
        if self.excluded_files:
            self.logger.warning("Files exluded from aggregations:")
            for f, e in self.excluded_files.items():
                self.logger.warning("'{f}': {e}".format(f=f, e=list(e)))

    dest_path = MooringsProductClassifier.dest_path

