import json
import os
import unittest
from unittest.mock import patch

import httpretty
from aodncore.pipeline import (PipelineFile, PipelineFileCollection,
                               PipelineFilePublishType)
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase, make_test_file

from aodndata.moorings.products_handler import MooringsProductsHandler, MooringsProductClassifier

TEST_ROOT = os.path.dirname(__file__)
GOOD_MANIFEST = os.path.join(TEST_ROOT, 'test_product.json_manifest')
PRODUCT_FILE = os.path.join(
    TEST_ROOT,
    'IMOS_ANMN-NRS_TZ_20181213_NRSROT_FV01_TEMP-aggregated-timeseries_END-20190523_C-20191218.nc'
)

GETFEATURE_FILE = os.path.join(TEST_ROOT, 'getFeature.json')
GETFEATURE_OLD_PRODUCTS_FILE = os.path.join(TEST_ROOT, 'getFeature_old_products.json')

with open(GETFEATURE_FILE) as f:
    TEST_GETFEATURE_JSON = f.read()

with open(GETFEATURE_OLD_PRODUCTS_FILE) as f:
    TEST_GETFEATURE_OLD_PRODUCTS_JSON = f.read()

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
        super(TestMooringsProductsHandler, self).setUp()

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_good_manifest(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.side_effect = [TEST_GETFEATURE_JSON,
                                                                      TEST_GETFEATURE_OLD_PRODUCTS_JSON]

        upload_broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        upload_broker.upload(INPUT_FILE_COLLECTION)

        handler = self.run_handler(GOOD_MANIFEST)
        self.assertCountEqual(INPUT_FILE_COLLECTION.get_attribute_list('dest_path'),
                              handler.input_file_collection.get_attribute_list('dest_path')
                              )
        self.assertEqual(len(handler.file_collection), 5)

        published_files = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                         PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(len(published_files), 3)
        for f in published_files:
            self.assertTrue(f.is_harvested and f.is_stored)

        deleted_files = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                       PipelineFilePublishType.DELETE_UNHARVEST)
        self.assertEqual(len(deleted_files), 2)
        for f in deleted_files:
            self.assertTrue(f.is_harvested and f.is_stored)

        self.assertEqual(len(handler.excluded_files), 1)

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

    def test_abos_aggregated_timeseries(self):
        expected_prefix = 'IMOS/ABOS/DA/aggregated_timeseries'
        filename = 'IMOS_ABOS-DA_TZ_20150519_EAC4700_FV01_TEMP-aggregated-timeseries_END-20180422_C-20191216.nc'
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

    def test_abos_hourly_timeseries_qc(self):
        expected_prefix = 'IMOS/ABOS/DA/hourly_timeseries'
        filename = 'IMOS_ABOS-DA_STZ_20110613_ITFTSL_FV02_hourly-timeseries_END-20151024_C-20191010.nc'
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

    def test_abos_hourly_timeseries_nonqc(self):
        expected_prefix = 'IMOS/ABOS/DA/hourly_timeseries'
        filename = 'IMOS_ABOS-DA_STZ_20110613_ITFTSL_FV02_hourly-timeseries-including-non-QC_END-20151024_C-20191010.nc'
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

    def test_abos_gridded_timeseries(self):
        expected_prefix = 'IMOS/ABOS/DA/gridded_timeseries'
        filename = 'IMOS_ABOS-DA_TZ_20150519_EAC4700_FV02_TEMP-gridded-timeseries_END-20180422_C-20191216.nc'
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

    def test_abos_sots_aggregated_timeseries(self):
        expected_prefix = 'IMOS/ABOS/SOTS/aggregated_timeseries'
        filename = 'IMOS_ABOS-SOTS_OZ_20170319_SOTS_FV01_DOX2-aggregated-timeseries_END-20171101_C-20190819.nc'
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
