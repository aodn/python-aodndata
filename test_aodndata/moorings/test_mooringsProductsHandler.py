import json
import os
import unittest
from unittest.mock import patch

from aodncore.pipeline import (PipelineFile, PipelineFileCollection,
                               PipelineFilePublishType)
from aodncore.pipeline.exceptions import InvalidFileContentError
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase, make_test_file

from aodndata.moorings.products_handler import MooringsProductsHandler, MooringsProductClassifier, get_product_type


# Input files used in tests
TEST_ROOT = os.path.dirname(__file__)
GOOD_MANIFEST = os.path.join(TEST_ROOT, 'test_product.json_manifest')
AGGREGATED_ONLY_MANIFEST = os.path.join(TEST_ROOT, 'test_product_aggregated.json_manifest')
VELOCITY_HOURLY_MANIFEST = os.path.join(TEST_ROOT, 'test_product_velocity_hourly.json_manifest')
BAD_VAR_MANIFEST = os.path.join(TEST_ROOT, 'test_product_bad_var.json_manifest')
PRODUCT_FILE = os.path.join(
    TEST_ROOT,
    'IMOS_ANMN-NRS_TZ_20181213_NRSROT_FV01_TEMP-aggregated-timeseries_END-20190523_C-20191218.nc'
)

# Load JSON files used to mock WFS responses
GETFEATURE_FILE = os.path.join(TEST_ROOT, 'getFeature.json')
GETFEATURE_OLD_PRODUCTS_FILE = os.path.join(TEST_ROOT, 'getFeature_old_products.json')
GETFEATURE_EMPTY_FILE = os.path.join(TEST_ROOT, 'getFeature_empty.json')

with open(GETFEATURE_FILE) as f:
    TEST_GETFEATURE_JSON = f.read()

with open(GETFEATURE_OLD_PRODUCTS_FILE) as f:
    TEST_GETFEATURE_OLD_PRODUCTS_JSON = f.read()

with open(GETFEATURE_EMPTY_FILE) as f:
    TEST_GETFEATURE_EMPTY_JSON = f.read()

# Create collection of input files for the products
# These will be uploaded to the mocked equivalent of S3 (where the real input files will be)
features = json.loads(TEST_GETFEATURE_JSON)['features']
INPUT_FILE_COLLECTION = PipelineFileCollection()
for f in features:
    pf = PipelineFile(
            os.path.join(TEST_ROOT, os.path.basename(f['properties']['url'])),
            dest_path=f['properties']['url']
    )
    pf.publish_type = PipelineFilePublishType.UPLOAD_ONLY
    INPUT_FILE_COLLECTION.add(pf)


class TestMooringsProductsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = MooringsProductsHandler
        upload_broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        upload_broker.upload(INPUT_FILE_COLLECTION)
        super().setUp()

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_all_products(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.side_effect = [TEST_GETFEATURE_JSON,
                                                                      TEST_GETFEATURE_OLD_PRODUCTS_JSON]

        handler = self.run_handler(GOOD_MANIFEST)
        self.assertCountEqual(INPUT_FILE_COLLECTION.get_attribute_list('dest_path'),
                              handler.input_file_collection.get_attribute_list('dest_path')
                              )

        expected_new_products = {'TEMP-aggregated-timeseries',
                                 'PSAL-aggregated-timeseries',
                                 'CHLF-aggregated-timeseries',
                                 'velocity-aggregated-timeseries',
                                 'hourly-timeseries',
                                 'hourly-timeseries-including-non-QC',
                                 'velocity-hourly-timeseries',
                                 'TEMP-gridded-timeseries'
                                 }
        expected_deleted_products = {'TEMP-aggregated-timeseries',
                                     'PSAL-aggregated-timeseries',
                                     'velocity-aggregated-timeseries',
                                     'hourly-timeseries'
                                     }

        self.assertEqual(len(handler.file_collection), len(expected_new_products) + len(expected_deleted_products))
        for f in handler.file_collection:
            self.assertTrue(f.is_harvested and f.is_stored)

        # check new product files
        published_files = (handler.file_collection
                                  .filter_by_attribute_id('publish_type', PipelineFilePublishType.HARVEST_UPLOAD)
                                  .get_attribute_list('name')
                           )
        self.assertEqual(len(published_files), len(expected_new_products))
        published_products = {get_product_type(f) for f in published_files}
        self.assertSetEqual(published_products, expected_new_products)

        # check deletion of previous versions
        deleted_files = (handler.file_collection
                                .filter_by_attribute_id('publish_type', PipelineFilePublishType.DELETE_UNHARVEST)
                                .get_attribute_list('name')
                         )
        self.assertEqual(len(deleted_files), len(expected_deleted_products))
        deleted_products = {get_product_type(f) for f in deleted_files}
        self.assertSetEqual(deleted_products, expected_deleted_products)

        # published and deleted files should never have the same name!
        self.assertEqual(set(), set(published_files) & set(deleted_files))

        # check input files excluded from the products
        self.assertEqual(len(handler.excluded_files), 1)

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_aggregated_only_no_old_files(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.side_effect = [TEST_GETFEATURE_JSON,
                                                                      TEST_GETFEATURE_EMPTY_JSON]

        handler = self.run_handler(AGGREGATED_ONLY_MANIFEST)

        expected_new_products = {'TEMP-aggregated-timeseries',
                                 'PSAL-aggregated-timeseries',
                                 'CHLF-aggregated-timeseries',
                                 }

        self.assertEqual(len(handler.file_collection), len(expected_new_products))
        for f in handler.file_collection:
            self.assertTrue(f.is_harvested and f.is_stored)
            self.assertIs(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertIn(get_product_type(f.name), expected_new_products)

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_velocity_hourly(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.side_effect = [TEST_GETFEATURE_JSON,
                                                                      TEST_GETFEATURE_OLD_PRODUCTS_JSON]

        handler = self.run_handler(VELOCITY_HOURLY_MANIFEST)

        expected_new_product = 'velocity-hourly-timeseries'
        self.assertEqual(len(handler.file_collection), 1)
        for f in handler.file_collection:
            self.assertTrue(f.is_harvested and f.is_stored)
            self.assertIs(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertEqual(get_product_type(f.name), expected_new_product)

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_bad_var(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.side_effect = [TEST_GETFEATURE_JSON,
                                                                      TEST_GETFEATURE_OLD_PRODUCTS_JSON]
        self.run_handler_with_exception(InvalidFileContentError, BAD_VAR_MANIFEST)

    def test_publish_product_nc(self):
        handler = self.run_handler(PRODUCT_FILE)
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertTrue(f.is_harvested and f.is_stored)
        self.assertEqual(
            os.path.join('IMOS/ANMN/NRS/NRSROT/aggregated_timeseries', os.path.basename(PRODUCT_FILE)),
            f.dest_path
        )


class TestMooringProductClassifier(HandlerTestCase):

    def test_anmn_aggregated_timeseries(self):
        expected_prefix = 'IMOS/ANMN/QLD/GBRLSL/aggregated_timeseries'
        filename = 'IMOS_ANMN-QLD_BZ_20121103_GBRLSL_FV01_CPHL-aggregated-timeseries_END-20140522_C-20191120.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'GBRLSL',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_anmn_hourly_timeseries_qc(self):
        expected_prefix = 'IMOS/ANMN/QLD/GBRLSL/hourly_timeseries'
        filename = 'IMOS_ANMN-QLD_BSTUZ_20071103_GBRLSL_FV02_hourly-timeseries_END-20140523_C-20191010.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'GBRLSL',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_anmn_hourly_timeseries_nonqc(self):
        expected_prefix = 'IMOS/ANMN/QLD/GBRLSL/hourly_timeseries'
        filename = 'IMOS_ANMN-QLD_BSTUZ_20071103_GBRLSL_FV02_hourly-timeseries-including-non-QC_END-20140523_C-20191010.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'GBRLSL',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_anmn_gridded_timeseries(self):
        expected_prefix = 'IMOS/ANMN/NRS/NRSROT/gridded_timeseries'
        filename = 'IMOS_ANMN-NRS_SZ_20081120_NRSROT_FV02_PSAL-gridded-timeseries_END-20190523_C-20191121.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'NRSROT',
                'source': 'mooring',
                'featureType': 'timeSeriesProfile'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_dwm_aggregated_timeseries(self):
        expected_prefix = 'IMOS/DWM/DA/aggregated_timeseries'
        filename = 'IMOS_DWM-DA_TZ_20150519_EAC4700_FV01_TEMP-aggregated-timeseries_END-20180422_C-20191216.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'EAC4700',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_dwm_hourly_timeseries_qc(self):
        expected_prefix = 'IMOS/DWM/DA/hourly_timeseries'
        filename = 'IMOS_DWM-DA_STZ_20110613_ITFTSL_FV02_hourly-timeseries_END-20151024_C-20191010.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'ITFTSL',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_dwm_hourly_timeseries_nonqc(self):
        expected_prefix = 'IMOS/DWM/DA/hourly_timeseries'
        filename = 'IMOS_DWM-DA_STZ_20110613_ITFTSL_FV02_hourly-timeseries-including-non-QC_END-20151024_C-20191010.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'ITFTSL',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_dwm_gridded_timeseries(self):
        expected_prefix = 'IMOS/DWM/DA/gridded_timeseries'
        filename = 'IMOS_DWM-DA_TZ_20150519_EAC4700_FV02_TEMP-gridded-timeseries_END-20180422_C-20191216.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'EAC4700',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)

    def test_dwm_sots_aggregated_timeseries(self):
        expected_prefix = 'IMOS/DWM/SOTS/aggregated_timeseries'
        filename = 'IMOS_DWM-SOTS_OZ_20170319_SOTS_FV01_DOX2-aggregated-timeseries_END-20171101_C-20190819.nc'
        testfile = os.path.join(self.temp_dir, filename)
        make_test_file(
            testfile, {
                'site_code': 'EAC4700',
                'source': 'mooring',
                'featureType': 'timeSeries'
            })
        dest_dir, dest_filename = os.path.split(
            MooringsProductsHandler.dest_path(testfile))
        self.assertEqual(dest_dir, expected_prefix)
        self.assertEqual(dest_filename, filename)


if __name__ == '__main__':
    unittest.main()
