import os
import unittest
from aodncore.pipeline import PipelineFilePublishType, FileType
from aodncore.testlib import HandlerTestCase
from aodndata.anfog.handlers import AnfogHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'IMOS_ANFOG_BCEOPSTUV_20160301T234750Z_SL286_FV01_timeseries_END-20160321T002220Z.nc')
TEST_DM_STATUS = os.path.join(TEST_ROOT,
                              'IMOS_ANFOG_BCEOPSTUV_20180204T050812Z_SL248_FV01_timeseries_END-20180226T222617Z.zip')
# NOT_A_NETCDF = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20170831T074045Z_VLMJ_FV01.nc')
# GOOD_RT = os.path.join(TEST_ROOT, '')
GOOD_DSTG = os.path.join(TEST_ROOT, 'DSTO_MD_CEPSTUV_20130706T122916Z_SL090_FV01_timeseries_END-20130715T040955Z.nc')
GOOD_ZIP_DM = os.path.join(TEST_ROOT, 'BassStrait20160302.zip')  # IMOS/ANFOG/slocum_glider/BassStrait20160302
GOOD_ZIP_RT = os.path.join(TEST_ROOT, 'Forster20180205.zip')  # IMOS/ANFOG/REALTIME/slocum_glider/Forster20180205


class TestAnfogHandler(HandlerTestCase):
    """It is recommended to inherit from the HandlerTestCase class (which is itself a subclass of the standard
       unittest.TestCase class). This provides some useful methods and properties to shortcut some common test
       scenarios.
    """

    def setUp(self):
        # set the handler_class attribute to your handler (as imported above)
        self.handler_class = AnfogHandler
        super(TestAnfogHandler, self).setUp()

    def test_good_anfog_dm_file(self):
        # we expect this to succeed, so if the handler experiences an error, it is considered a
        # "failed test"
        handler = self.run_handler(GOOD_NC, check_params={'checks': ['cf']})
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        # self.assertEqual(f.name, os.path.basename(GOOD_NC))
        # self.assertEqual(f.dest_path,
        #                  'IMOS/ANFOG/slocum_glider/BassStrait20160302/'
        #                  'IMOS_ANFOG_BCEOPSTUV_20160301T234750Z_SL286_FV01_timeseries_END-20160321T002220Z.nc')
        self.assertTrue(f.is_stored)

    def test_good_anfog_dm_zip(self):
        # we expect this to succeed, so if the handler experiences an error, it is considered a
        # "failed test"
        handler = self.run_handler(TEST_DM_STATUS, check_params={'checks': ['cf']})

        # self.assertEqual(len(handler.file_collection), 3)

        # raw = handler.file_collection.filter_by_attribute_value('extension', '.zip')
        # jpeg = handler.file_collection.filter_by_attribute_value('extension', '.jpg')

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        # j = jpeg[0]
        # self.assertEqual(j.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        # self.assertEqual(j.dest_path,
        #                  'IMOS/ANFOG/slocum_glider/BassStrait20160302/' + j.name)
        # self.assertTrue(j.is_stored)
        #
        # r = raw[0]
        # self.assertEqual(r.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        # self.assertEqual(r.archive_path,
        #                  'IMOS/ANFOG/slocum_glider/BassStrait20160302/' + r.name)
        # self.assertTrue(r.is_archived)
        for nc in nc_file:
            self.assertEqual(nc.dest_path,
                             'IMOS/ANFOG/slocum_glider/Forster20180205/' + nc.name)
            self.assertTrue(nc.is_stored)

    def test_good_anfog_rt_zip(self):
        # we expect this to succeed, so if the handler experiences an error, it is considered a
        # "failed test"
        handler = self.run_handler(GOOD_ZIP_RT)


        png = handler.file_collection.filter_by_attribute_regex('extension', '.png')

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        p = png[0]
        self.assertEqual(p.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertEqual(p.dest_path,
                         'IMOS/ANFOG/REALTIME/slocum_glider/Forster20180205/' + p.name)

        self.assertTrue(p.is_stored)

        for nc in nc_file:
            self.assertEqual(nc.dest_path,
                             'IMOS/ANFOG/REALTIME/slocum_glider/Forster20180205/' + nc.name)
            self.assertTrue(nc.is_stored)

    def test_dstg(self):
        # test future Reef Map processing
        handler = self.run_handler(GOOD_DSTG)
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         'Department_of_Defence/DSTG/slocum_glider/TalismanSaberB20130706/' + f.name)
        self.assertTrue(f.is_stored)

    def test_good_file_with_compliance_check(self):
        # we also expect this to succeed, since the test file is known be CF compliant
        self.run_handler(GOOD_NC, check_params={'checks': ['cf', 'imos:1.4']})


if __name__ == '__main__':
    unittest.main()
