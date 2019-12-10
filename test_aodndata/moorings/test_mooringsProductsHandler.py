import json
import os
import shutil
import unittest
from tempfile import mkdtemp

import httpretty
from aodncore.pipeline import (PipelineFile, PipelineFileCollection,
                               PipelineFilePublishType)
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import HandlerTestCase, make_test_file

from aodndata.moorings.products_handler import MooringsProductsHandler

TEST_ROOT = os.path.dirname(__file__)
GOOD_MANIFEST = os.path.join(TEST_ROOT, 'test_product.json_manifest')

GETCAPABILITIES_FILE = os.path.join(TEST_ROOT, 'getCapabilities.xml')
GETFEATURE_FILE = os.path.join(TEST_ROOT, 'getFeature.json')

with open(GETCAPABILITIES_FILE) as f:
    TEST_GETCAPABILITIES_RESPONSE = httpretty.Response(f.read())

with open(GETFEATURE_FILE) as f:
    TEST_GETFEATURE_JSON = f.read()
TEST_GETFEATURE_RESPONSE = httpretty.Response(TEST_GETFEATURE_JSON)

features = json.loads(TEST_GETFEATURE_JSON)['features']
INPUT_FILE_COLLECTION = PipelineFileCollection()
for f in features:
    pf = PipelineFile(os.path.join(TEST_ROOT,
                                   os.path.basename(f['properties']['url'])),
                      dest_path=f['properties']['url'])
    pf.publish_type = PipelineFilePublishType.UPLOAD_ONLY
    INPUT_FILE_COLLECTION.add(pf)


class TestMooringsProductsHandler(HandlerTestCase):
    def setUp(self):
        self.tempdir = mkdtemp()
        self.handler_class = MooringsProductsHandler
        super(TestMooringsProductsHandler, self).setUp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @httpretty.activate
    def test_good_manifest(self):
        httpretty.register_uri(
            httpretty.GET,
            self.config.pipeline_config['global']['wfs_url'],
            responses=[
                TEST_GETCAPABILITIES_RESPONSE, TEST_GETCAPABILITIES_RESPONSE,
                TEST_GETFEATURE_RESPONSE
            ])
        # TODO: remove double TEST_GETCAPABILITIES_RESPONSE above, when it's no longer needed

        upload_broker = get_storage_broker(
            self.config.pipeline_config['global']['upload_uri'])
        upload_broker.upload(INPUT_FILE_COLLECTION)

        handler = self.run_handler(GOOD_MANIFEST)
        self.assertEqual(len(handler.excluded_files), 1)

    def test_aodn_moorings_aggregated(self):
        expected_prefix = 'IMOS/ANMN/QLD/GBRLSL/aggregated_timeseries'
        filename = 'IMOS_ANMN-QLD_BZ_20121103_GBRLSL_FV01_CPHL-aggregated-timeseries_END-20140522_C-20191120.nc'
        testfile = os.path.join(self.tempdir, filename)
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

    def test_aodn_moorings_hourly_timeseries_qc(self):
        expected_prefix = 'IMOS/ANMN/QLD/GBRLSL/hourly_timeseries'
        filename = 'IMOS_ANMN-QLD_BSTUZ_20071103_GBRLSL_FV02_hourly-timeseries_END-20140523_C-20191010.nc'
        testfile = os.path.join(self.tempdir, filename)
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

    def test_aodn_moorings_hourly_timeseries_nonqc(self):
        expected_prefix = 'IMOS/ANMN/QLD/GBRLSL/hourly_timeseries'
        filename = 'IMOS_ANMN-QLD_BSTUZ_20071103_GBRLSL_FV02_hourly-timeseries-including-non-QC_END-20140523_C-20191010.nc'
        testfile = os.path.join(self.tempdir, filename)
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

    def test_aodn_moorings_gridded_timeseries(self):
        expected_prefix = 'IMOS/ANMN/NRS/NRSROT/gridded_timeseries'
        filename = 'IMOS_ANMN-NRS_SZ_20081120_NRSROT_FV02_PSAL-gridded-timeseries_END-20190523_C-20191121.nc'
        testfile = os.path.join(self.tempdir, filename)
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


if __name__ == '__main__':
    unittest.main()
