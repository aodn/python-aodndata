import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_asf_sst import SoopAsfSstHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC_ASF_FMT = os.path.join(TEST_ROOT,
                               'IMOS_SOOP-ASF_FMT_20130118T012200Z_VLHJ_FV02_C-20150914T042207Z.nc')
GOOD_NC_ASF_MT = os.path.join(TEST_ROOT,
                              'IMOS_SOOP-ASF_MT_20130117T215000Z_VLHJ_FV01_C-20130307T042609Z.nc')
GOOD_NC_SST = os.path.join(TEST_ROOT,
                           'IMOS_SOOP-SST_T_20150127T103500Z_9V2768_FV01_C-20150624T041651Z.nc')


class TestSoopAsfSstHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopAsfSstHandler
        super(TestSoopAsfSstHandler, self).setUp()

    def test_good_netcdf_asf_fmt(self):
        handler = self.run_handler(GOOD_NC_ASF_FMT,
                                     include_regexes=['IMOS_SOOP-ASF_FMT_.*\.nc']
                                     )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.FORMAT_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC_ASF_FMT))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-ASF/VLHJ_Southern-Surveyor/flux_product/2013/IMOS_SOOP-ASF_FMT_20130118T012200Z_VLHJ_FV02_C-20150914T042207Z.nc')
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_good_netcdf_asf_mt(self):
        handler = self.run_handler(GOOD_NC_ASF_MT,
                                     include_regexes=['IMOS_SOOP-ASF_MT_.*\.nc']
                                     )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.FORMAT_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC_ASF_MT))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-ASF/VLHJ_Southern-Surveyor/meteorological_sst_observations/2013/IMOS_SOOP-ASF_MT_20130117T215000Z_VLHJ_FV01_C-20130307T042609Z.nc')
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_good_netcdf_sst(self):
        handler = self.handler_class(GOOD_NC_SST,
                                     include_regexes=['IMOS_SOOP-SST_.*\.nc']
                                     )
        handler.run()
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.FORMAT_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC_SST))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-SST/9V2768_RTM-Wakmatha/2015/IMOS_SOOP-SST_T_20150127T103500Z_9V2768_FV01_C-20150624T041651Z.nc')
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
