import os
import unittest
from aodncore.pipeline import PipelineFilePublishType, PipelineFileCheckType
from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_co2 import SoopCo2Handler
from aodncore.pipeline.exceptions import ComplianceCheckFailedError

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20170126T023510Z_VNAA_FV01.nc')
NOT_A_NETCDF = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20170831T074045Z_VLMJ_FV01.nc')
GOOD_RT = os.path.join(TEST_ROOT, 'IN_2018-022-0000dat.txt')
GOOD_FRMAP = os.path.join(TEST_ROOT, 'FutureReefMap_GST_20150518T124011Z_9V2768_FV01.nc')
GOOD_ZIP = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20170126T023510Z_VNAA_FV01.zip')


# GOOD_RT = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20180122T000135Z_VLMJ_FV00_END-20180123T000058Z.nc')

class TestSoopCo2Handler(HandlerTestCase):
    """It is recommended to inherit from the HandlerTestCase class (which is itself a subclass of the standard
       unittest.TestCase class). This provides some useful methods and properties to shortcut some common test
       scenarios.
    """

    # This is a "boilerplate" method that must appear in each test case in order to correctly inherit from the HandlerTestCase class
    def setUp(self):
        # set the handler_class attribute to your handler (as imported above)
        self.handler_class = SoopCo2Handler
        super(TestSoopCo2Handler, self).setUp()

    def test_good_co2_file(self):
        # we expect this to succeed, so if the handler experiences an error, it is considered a
        # "failed test"
        handler = self.run_handler(GOOD_NC, check_params={'checks': ['cf']})
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/2017/AA1617_V3/IMOS_SOOP-CO2_GST_20170126T023510Z_VNAA_FV01.nc')
        self.assertTrue(f.is_stored)

    def test_good_co2rt_file(self):
        # we expect this to succeed, so if the handler experiences an error, it is considered a
        # "failed test"
        handler = self.run_handler(GOOD_RT)

        self.assertEqual(len(handler.file_collection), 1)
        txt_file = handler.file_collection.filter_by_attribute_value('extension', '.txt')
        nc_file = handler.file_collection.filter_by_attribute_value('extension', '.nc')

        for t in txt_file:
            self.assertEqual(t.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
            self.assertEqual(t.archive_path,
                             'IMOS/SOOP/SOOP-CO2/VLMJ_Investigator/REALTIME/2018/1/' + t.name)
            self.assertTrue(t.is_archived)

        for nc in nc_file:
            self.assertEqual(nc.dest_path,
                             'IMOS/SOOP/SOOP-CO2/VLMJ_Investigator/REALTIME/2018/1/' + nc.name)
            self.assertTrue(nc.is_stored)

    def test_frmap_file(self):
        # test future Reef Map processing
        handler = self.run_handler(GOOD_FRMAP)
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_FRMAP))
        self.assertEqual(f.dest_path,
                         'Future_Reef_MAP/underway/RTM-Wakmatha/2015/WK201505N/FutureReefMap_GST_20150518T124011Z_9V2768_FV01.nc')
        self.assertTrue(f.is_stored)

    def test_good_nc_zip(self):

        handler = self.handler_class(GOOD_ZIP,
                                     check_params={'checks': ['cf']}
                                     )
        handler.run()
        self.assertEqual(len(handler.file_collection), 3)

        nc_files = handler.file_collection.filter_by_attribute_value('extension', '.nc')

        for f in nc_files:
            self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
            self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertEqual(f.name, os.path.basename(GOOD_NC))
            self.assertEqual(f.dest_path,
                             'IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/2017/AA1617_V3/' + f.name
                             )

        non_nc = handler.file_collection.filter_by_attribute_regex('extension', '[.](?!nc$)$')
        for f in non_nc:
            self.assertEqual(f.dest_path,
                             'IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/2017/AA1617_V3/' + f.name)
            self.assertEqual(f.check_type, PipelineFileCheckType.NONEMPTY_CHECK)
            self.assertEqual(f.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

    def test_good_file_with_compliance_check(self):
        # we also expect this to succeed, since the test file is known be CF compliant
        self.run_handler(GOOD_NC, check_params={'checks': ['cf']})


if __name__ == '__main__':
            unittest.main()
