import json
import os
import re

from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, And

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, PipelineFile
from aodncore.pipeline.exceptions import (InvalidFileContentError, InvalidFileNameError, InvalidFileFormatError,
                                          MissingFileError, PipelineSystemError)
from aodncore.pipeline.files import RemotePipelineFileCollection
from aodncore.util.wfs import ogc_filter_to_string

from aodntools.timeseries_products.aggregated_timeseries import main_aggregator

from aodndata.moorings.classifiers import MooringsFileClassifier


AGGREGATED_VARIABLE_PATTERN = re.compile(r'FV01_([A-Z0-9-]+)-aggregated')


class MooringsProductClassifier(MooringsFileClassifier):
    @classmethod
    def _get_data_category(cls, input_file):
        if 'aggregated-timeseries' in input_file:
            return 'aggregated_timeseries'
        elif 'hourly-timeseries' in input_file:
            return 'hourly_timeseries'
        elif 'gridded-timeseries' in input_file:
            return 'gridded_timeseries'
        else:
            raise InvalidFileNameError(
                "Could not determine data category from {name}".format(name=input_file)
            )

    @classmethod
    def _get_product_level(cls, input_file):
        return ''

    @classmethod
    def dest_path(cls, input_file):
        """
        Destination object path for a moorings netCDF file. Of the form:

          'IMOS/<facility>/<subfacility>/<site_code>/<data_category>/<product_level>'

        where
        <facility> = 'ANMN' or 'ABOS'
        <subfacility> is the sub-facility code ('NRS', 'NSW', 'SOTS', etc...)
        <site_code> is the value of the site_code global attribute
        <data_category> is a broad category like 'Temperature', 'CTD_profiles', etc...
        <product_level> is
         - 'non-QC' for FV00 files
         - empty for FV01 files
         - 'burst-averaged' or 'gridded' as appropriate, for FV02 files
        The basename of the input file is appended.

        """
        name_fields = cls._get_file_name_fields(input_file)

        dir_list = [cls.PROJECT]
        dir_list.extend(cls._get_facility(input_file))

        if input_file.endswith('.nc'):
            if 'ABOS' not in input_file:
                dir_list.append(cls._get_site_code(input_file))
            dir_list.append(cls._get_data_category(input_file))
            dir_list.append(cls._get_product_level(input_file))

        else:
            raise InvalidFileFormatError(
                "Don't know where to put file '{name}' (unhandled extension)".format(name=input_file)
            )

        dir_list.append(os.path.basename(input_file))

        return cls._make_path(dir_list)


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
        self.excluded_files = dict()

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

    def get_wfs_features(self, filter_list, propertyname='*'):
        """Query the file index WFS layer with the given filters and return a list of features.

        :param filter_list: list of filters to apply (owslib.fes.OgcExpression instances)
        :param propertyname: str or list or property name(s) to return
        :return: list of features from the parsed GetFeature response
        """

        ogc_filter = ogc_filter_to_string(And(filter_list))

        # Note I need to access _wfs_broker to be able to use query_urls_for_layer() with a filter,
        # as the corresponding StateQuery method doesn't accept additional kwargs.
        # TODO: find out why this calls getCapabilities twice (and takes 40s even when response mocked with httpretty)
        # TODO: replace ._wfs_broker.getfeature_dict() with .getfeature_dict() once aodncore has been updated
        wfs_response = self.state_query._wfs_broker.getfeature_dict(typename=[self.FILE_INDEX_LAYER],
                                                                    filter=ogc_filter,
                                                                    propertyname=propertyname
                                                                    )
        if not wfs_response or 'features' not in wfs_response:
            raise PipelineSystemError("Invalid WFS response received from '{wfs_url}'".format(
                wfs_url=self.config.pipeline_config['global'].get('wfs_url')
            ))

        return wfs_response['features']

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
        wfs_features = self.get_wfs_features(filter_list, propertyname=['url', 'variables'])
        if not wfs_features:
            raise MissingFileError("No input files found for site '{self.product_site_code}'".format(self=self))

        self.input_file_variables = {f['properties']['url']: f['properties']['variables'].split(', ')
                                     for f in wfs_features
                                     }
        self.input_file_collection = RemotePipelineFileCollection(self.input_file_variables.keys())

        # Download input files to local cache.
        self.logger.info("Downloading {n} input files".format(n=len(self.input_file_collection)))
        self.input_file_collection.download(self._upload_store_runner.broker, self.temp_dir)
        # TODO: Replace temp_dir above with cache_dir?

    def _get_old_product_files(self):
        """Get a list of the currently published aggregated_timeseries files for the site being processed."""

        filter_list = [PropertyIsEqualTo(propertyname='site_code', literal=self.product_site_code),
                       PropertyIsEqualTo(propertyname='data_category', literal='aggregated_timeseries')
                       ]
        wfs_features = self.get_wfs_features(filter_list, propertyname=['url'])

        self.old_product_files = {}
        for f in wfs_features:
            product_url = f['properties']['url']
            var_match = AGGREGATED_VARIABLE_PATTERN.search(product_url)
            if not var_match:
                raise InvalidFileNameError(
                    "Could not determine variable of interest for '{product_url}'".format(product_url=product_url)
                )
            variable_of_interest = var_match.group(1).replace('-', '_')
            if variable_of_interest not in self.old_product_files:
                self.old_product_files[variable_of_interest] = [product_url]
            else:
                self.old_product_files[variable_of_interest].append(product_url)

            self.logger.info(
                "Old file for {variable_of_interest}: '{product_url}'".format(variable_of_interest=variable_of_interest,
                                                                              product_url=product_url)
                )

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
                    if f not in self.excluded_files:
                        self.excluded_files[f] = set(e)
                    else:
                        self.excluded_files[f].update(e)

            product_file = PipelineFile(product_url, file_update_callback=self._file_update_callback)
            product_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(product_file)

            self._cleanup_previous_version(product_file.name, var)

    def _cleanup_previous_version(self, product_name, var):
        """Delete any previously published version(s) of the product for this variable file.
        Ignores cases where the previous version has exactly the same file name, as this will simply be overwritten.

        :param product_name: Name of the newly generated product
        :param var: Name of the variable of interest
        """
        for old_product_url in self.old_product_files.get(var, []):
            if os.path.basename(old_product_url) != product_name:
                old_file = PipelineFile(old_product_url, dest_path=old_product_url, is_deletion=True,
                                        late_deletion=True, file_update_callback=self._file_update_callback)
                old_file.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
                self.file_collection.add(old_file)

    def preprocess(self):
        """Collect available input files and create the products, adding them to the collection to be published."""

        self._read_manifest()
        self.logger.info(
            "Creating products for site {self.product_site_code}, variables {self.product_variables}".format(self=self)
        )

        self._get_input_files()
        self._get_old_product_files()

        # TODO: Run compliance checks and remove non-compliant files from the input list (log them).

        self._make_aggregated_timeseries()

        # TODO: Include the list of excluded files as another table in the notification email (instead of the log)
        if self.excluded_files:
            self.logger.warning("Files exluded from aggregations:")
            for f, e in self.excluded_files.items():
                self.logger.warning("'{f}': {e}".format(f=f, e=list(e)))

    dest_path = MooringsProductClassifier.dest_path

