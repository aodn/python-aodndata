import json
import os
import re

from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, And, Or

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, PipelineFile, FileType
from aodncore.pipeline.exceptions import (InvalidFileContentError, InvalidFileNameError, InvalidFileFormatError,
                                          MissingFileError, PipelineSystemError)
from aodncore.pipeline.files import RemotePipelineFileCollection
from aodncore.util.wfs import ogc_filter_to_string

from aodntools.timeseries_products.aggregated_timeseries import main_aggregator
from aodntools.timeseries_products.hourly_timeseries import hourly_aggregator
from aodntools.timeseries_products.gridded_timeseries import grid_variable
from aodntools.timeseries_products.velocity_aggregated_timeseries import velocity_aggregated
from aodntools.timeseries_products.velocity_hourly_timeseries import velocity_hourly_aggregated

from aodndata.moorings.classifiers import MooringsFileClassifier


PRODUCT_TYPE_PATTERN = re.compile(r'FV0[12]_([^_]+)_END')
DOWNLOAD_URL_PREFIX = "https://s3-ap-southeast-2.amazonaws.com/imos-data/"
OPENDAP_URL_PREFIX = "http://thredds.aodn.org.au/thredds/dodsC/"


def get_product_type(file_path):
    """Return a product type label for the given file (extracted from the file name).
    For example "PSAL-aggregated-timeseries", or "hourly-timeseries".

    :param file_path: str path or name of file
    :returns: str product type label
    """
    file_name = os.path.basename(file_path)
    name_match = PRODUCT_TYPE_PATTERN.search(file_name)
    if not name_match:
        raise InvalidFileNameError(
            "Could not extract produt type from '{file_name}'".format(file_name=file_name)
        )
    return name_match.group(1)


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
        Destination object path for a moorings product file. Of the form:

          'IMOS/ANMN/<subfacility>/<site_code>/<data_category>', or
          'IMOS/ABOS/<subfacility>/<data_category>'

        where
        <subfacility> is the sub-facility code ('NRS', 'NSW', 'SOTS', etc...)
        <site_code> is the value of the site_code global attribute
        <data_category> is 'aggregated_timeseries', 'hourly_timeseries', or 'gridded_timeseries'
        The basename of the input file is appended.

        """
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
    """Handler to create and publish products from moorings files.

    The input file is a JSON document containing a site_code and a list of variables. The handler will then create
    the products for each variable at that site, using all the relevant input files available on S3.

    The structure of the JSON document will be something like this:
    {
        "site_code": "NRSMAI",
        "variables": ["TEMP", "PSAL", "DOX1", "DOX2", "CPHL"]
    }

    The handler can also publish product netCDF files that have been generated externally.
    """

    FILE_INDEX_LAYER = 'imos:moorings_all_map'
    VALID_PRODUCTS = {'aggregated', 'hourly', 'gridded', 'velocity_aggregated', 'velocity_hourly'}

    def __init__(self, *args, **kwargs):
        super(MooringsProductsHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.json_manifest', '.nc', '.zip']
        self.product_site_code = None
        self.product_variables = None
        self.products_to_create = self.VALID_PRODUCTS
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
        if 'products' in manifest:
            invalid_products = set(manifest['products']) - self.VALID_PRODUCTS
            if invalid_products:
                raise InvalidFileContentError(
                    "invalid product(s) {invalid_products} requested "
                    "in manifest file '{self.input_file}'".format(invalid_products=invalid_products, self=self)
                )
            self.products_to_create = set(manifest['products'])

        # Even if only the gridded product is explicitly requested, we need to re-generate and publish the hourly too,
        # as it is the input file for the gridded.
        if 'gridded' in self.products_to_create:
            self.products_to_create.add('hourly')

    @property
    def product_common_kwargs(self):
        """Shortcut dictionary for kwargs common to all product generating codes"""
        return {'input_dir': self.temp_dir,
                'output_dir': self.products_dir,
                'download_url_prefix': DOWNLOAD_URL_PREFIX,
                'opendap_url_prefix': OPENDAP_URL_PREFIX
                }

    def get_wfs_features(self, filter_list, propertyname='*'):
        """Query the file index WFS layer with the given filters and return a list of features.

        :param filter_list: list of filters to apply (owslib.fes.OgcExpression instances)
        :param propertyname: str or list or property name(s) to return
        :return: list of features from the parsed GetFeature response
        """

        ogc_filter = ogc_filter_to_string(And(filter_list))
        wfs_response = self.state_query.query_wfs_getfeature_dict(typename=[self.FILE_INDEX_LAYER],
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
        """Get a list of the currently published product files for the site being processed."""

        product_data_category = Or([PropertyIsEqualTo(propertyname='data_category', literal='aggregated_timeseries'),
                                    PropertyIsEqualTo(propertyname='data_category', literal='hourly_timeseries'),
                                    PropertyIsEqualTo(propertyname='data_category', literal='gridded_timeseries')]
                                   )
        filter_list = [PropertyIsEqualTo(propertyname='site_code', literal=self.product_site_code),
                       product_data_category
                       ]
        wfs_features = self.get_wfs_features(filter_list, propertyname=['url'])

        self.old_product_files = {}
        for f in wfs_features:
            product_url = f['properties']['url']
            product_type = get_product_type(product_url)
            if product_type not in self.old_product_files:
                self.old_product_files[product_type] = [product_url]
            else:
                self.old_product_files[product_type].append(product_url)

            self.logger.info(
                "Old file for {product_type}: '{product_url}'".format(product_type=product_type,
                                                                      product_url=product_url)
            )

    def _log_excluded_files(self, errors):
        """Keep track of any input files that were excluded from the product and log a brief warning."""
        if errors:
            self.logger.warning("{n} files were excluded from the product.".format(n=len(errors)))
            for f, e in errors.items():
                if f not in self.excluded_files:
                    self.excluded_files[f] = set(e)
                else:
                    self.excluded_files[f].update(e)

    def _add_to_collection(self, product_url):
        """Add a new product file to the file_collection to be harvested and uploaded."""
        product_file = PipelineFile(product_url, file_update_callback=self._file_update_callback)
        product_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
        self.file_collection.add(product_file)

    def _input_list_for_variables(self, *variables):
        """Return a list of input files containing any of the given variables"""
        input_list = [f for f, f_vars in self.input_file_variables.items()
                      if any(v in f_vars for v in variables)
                      ]
        return input_list

    def _make_aggregated_timeseries(self):
        """For each variable, generate aggregated timeseries product and add to file_collection."""

        for var in self.product_variables:
            # Filter input_list to the files relevant for this var
            input_list = self._input_list_for_variables(var)
            if not input_list:
                raise InvalidFileContentError("No files to aggregate for {var}".format(var=var))
            self.logger.info("Aggregating {var} ({n} files)".format(var=var, n=len(input_list)))

            product_url, errors = main_aggregator(input_list, var, self.product_site_code,
                                                  **self.product_common_kwargs)
            self._log_excluded_files(errors)
            self._add_to_collection(product_url)
            self._cleanup_previous_version(os.path.basename(product_url))

    def _make_velocity_aggregated_timeseries(self):
        """Generate the velocity aggregated timeseries product and add to file_collection."""

        # Filter input list to just the velocity files, i.e. files with the variables
        # UCUR ("eastward_sea_water_velocity") or VCUR ("northward_sea_water_velocity")
        input_list = self._input_list_for_variables('UCUR', 'VCUR')
        if not input_list:
            raise InvalidFileContentError("No velocity files to aggregate")
        self.logger.info("Aggregating velocity ({n} files)".format(n=len(input_list)))

        product_url, errors = velocity_aggregated(input_list, self.product_site_code, **self.product_common_kwargs)

        self._log_excluded_files(errors)
        self._add_to_collection(product_url)
        self._cleanup_previous_version(os.path.basename(product_url))

    def _make_hourly_timeseries(self):
        """Generate hourly products for the site and add to file_collection."""

        # Filter input_list to the files relevant for this var
        input_list = self.input_file_collection.get_attribute_list('local_path')
        self.logger.info("Creating hourly products from {n} input files".format(n=len(input_list)))

        # create two versions of the product, one with only good data (flags 1 & 2),
        # and one also including non-QC'd data (flag 0)
        for qc_flags in ((1, 2), (0, 1, 2)):

            product_url, errors = hourly_aggregator(input_list, self.product_site_code, qc_flags,
                                                    **self.product_common_kwargs)

            self._log_excluded_files(errors)
            self._add_to_collection(product_url)
            self._cleanup_previous_version(os.path.basename(product_url))

    def _make_velocity_hourly_timeseries(self):
        """Generate velocity hourly product for the site and add to file_collection."""

        # Filter input list to just the velocity files, i.e. files with the variables
        # UCUR ("eastward_sea_water_velocity") or VCUR ("northward_sea_water_velocity")
        input_list = self._input_list_for_variables('UCUR', 'VCUR')
        if not input_list:
            raise InvalidFileContentError("No velocity files to aggregate")
        self.logger.info("Creating velocity hourly products from {n} input files".format(n=len(input_list)))

        product_url, errors = velocity_hourly_aggregated(input_list, self.product_site_code,
                                                         **self.product_common_kwargs)

        self._log_excluded_files(errors)
        self._add_to_collection(product_url)
        self._cleanup_previous_version(os.path.basename(product_url))

    def _make_gridded_timeseries(self):
        """Generage TEMP gridded product from the new hourly product file."""

        # Find the full QC'd hourly product to use as input
        hourly_files = (self.file_collection
                            .filter_by_attribute_regex('name', r'.*FV02_hourly-timeseries_END')
                            .filter_by_attribute_id('publish_type', PipelineFilePublishType.HARVEST_UPLOAD)
                        )
        if len(hourly_files) != 1:
            raise MissingFileError("Don't have an hourly-timeseries file as input for gridded product!")
        hourly_file = hourly_files[0]
        self.logger.info("Creating gridded product from '{hourly_file.name}'".format(hourly_file=hourly_file))

        # create a local symlink in temp_dir which includes the final S3 id (dest_path) so that
        # it is recorded in the gridded file's metadata
        hourly_file.dest_path = self.dest_path(hourly_file.local_path)
        hourly_temp_path = os.path.join(self.temp_dir, hourly_file.dest_path)
        os.makedirs(os.path.dirname(hourly_temp_path))
        os.symlink(hourly_file.local_path, hourly_temp_path)

        # create gridded file and add to collection for publication
        product_url = grid_variable(hourly_file.dest_path, 'TEMP', **self.product_common_kwargs)

        self._add_to_collection(product_url)
        self._cleanup_previous_version(os.path.basename(product_url))

    def _cleanup_previous_version(self, product_filename):
        """Identify any previously published version(s) of the given product file and mark them for deletion.
        Ignores cases where the previous version has exactly the same file name, as this will simply be overwritten.

        :param product_filename: File name of the newly generated product
        """
        product_type = get_product_type(product_filename)
        for old_product_url in self.old_product_files.get(product_type, []):
            if os.path.basename(old_product_url) != product_filename:
                # Add the previous version as a "late deletion". It will be deleted during the handler's `publish`
                # step after (and only if) all new files have been successfully published.
                old_file = PipelineFile(old_product_url, dest_path=old_product_url, is_deletion=True,
                                        late_deletion=True, file_update_callback=self._file_update_callback)
                old_file.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
                self.file_collection.add(old_file)

    def preprocess(self):
        """If the input is a manifest file, collect available input files and
        create the products, adding them to the collection to be published.
        """

        if self.file_type is not FileType.JSON_MANIFEST:
            return

        self._read_manifest()
        self.logger.info(
            "Creating products for site {self.product_site_code}, variables {self.product_variables}".format(self=self)
        )

        self._get_input_files()
        self._get_old_product_files()

        # TODO: Run compliance checks and remove non-compliant files from the input list (log them).

        if 'aggregated' in self.products_to_create:
            self._make_aggregated_timeseries()

        if 'velocity_aggregated' in self.products_to_create:
            self._make_velocity_aggregated_timeseries()

        if 'hourly' in self.products_to_create:
            self._make_hourly_timeseries()

        if 'velocity_hourly' in self.products_to_create:
            self._make_velocity_hourly_timeseries()

        if 'gridded' in self.products_to_create:
            self._make_gridded_timeseries()

        # TODO: Include the list of excluded files as another table in the notification email (instead of the log)
        if self.excluded_files:
            self.logger.warning("Files exluded from some of the products generated:")
            for f, e in self.excluded_files.items():
                self.logger.warning("'{f}': {e}".format(f=f, e=list(e)))

    dest_path = MooringsProductClassifier.dest_path
