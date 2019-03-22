import os
import unittest

from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFileCheckType
from aodncore.testlib import HandlerTestCase

from aodndata.soop.soop_co2 import SoopCo2Handler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20170126T023510Z_VNAA_FV01.nc')
GOOD_FRMAP = os.path.join(TEST_ROOT, 'FutureReefMap_GST_20150518T124011Z_9V2768_FV01.nc')
GOOD_ZIP = os.path.join(TEST_ROOT, 'IMOS_SOOP-CO2_GST_20170126T023510Z_VNAA_FV01.zip')
GOOD_RT_IN_TXT = os.path.join(TEST_ROOT, 'IN_2018-022-0000dat.txt')
GOOD_RT_AA_TXT = os.path.join(TEST_ROOT, 'AA_2019-032-0001dat.txt')

ship_callsign_ls = {'VNAA': 'Aurora-Australis',
                    '9V2768': 'RTM-Wakmatha',
                    'VLMJ': 'Investigator'
                    }


class TestSoopCo2Handler(HandlerTestCase):
    """It is recommended to inherit from the HandlerTestCase class (which is itself a subclass of the standard
       unittest.TestCase class). This provides some useful methods and properties to shortcut some common test
       scenarios.
    """
    def setUp(self):
        # set the handler_class attribute to your handler (as imported above)
        self.handler_class = SoopCo2Handler
        super(TestSoopCo2Handler, self).setUp()

    def test_good_co2_nc(self):
        handler = self.run_handler(GOOD_NC,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls}
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path,
                         'IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/2017/AA1617_V3/IMOS_SOOP-CO2_GST_20170126T023510Z_VNAA_FV01.nc')
        self.assertTrue(f.is_stored)
        self.assertTrue(f.is_checked)

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
        handler = self.run_handler(GOOD_ZIP,
                                   check_params={'checks': ['cf']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls}
                                     )
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

    def test_good_rt_in_txt(self):
        handler = self.run_handler(GOOD_RT_IN_TXT,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls},
                                   check_params={'checks': ['cf', 'imos:1.4']})

        f_txt = handler.file_collection.filter_by_attribute_value('extension', '.txt')[0]
        self.assertEqual(f_txt.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-CO2/VLMJ_Investigator/REALTIME/2018/1/'
                         'IMOS_SOOP-CO2_GST_20180122T000135Z_VLMJ_FV00_END-20180123T000058Z.nc',
                         f_nc.dest_path)

        self.assertEqual(f_txt.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-CO2/VLMJ_Investigator/REALTIME/2018/1/',
                                      os.path.basename(GOOD_RT_IN_TXT)),
                         f_txt.archive_path)
        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_good_rt_aa_txt(self):
        handler = self.run_handler(GOOD_RT_AA_TXT,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls},
                                   check_params={'checks': ['cf', 'imos:1.4']})

        f_txt = handler.file_collection.filter_by_attribute_value('extension', '.txt')[0]
        self.assertEqual(f_txt.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/REALTIME/2019/2/'
                         'IMOS_SOOP-CO2_GST_20190201T000131Z_VNAA_FV00_END-20190202T000030Z.nc',
                         f_nc.dest_path)

        self.assertEqual(f_txt.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/REALTIME/2019/2/',
                                      os.path.basename(GOOD_RT_AA_TXT)),
                         f_txt.archive_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)


if __name__ == '__main__':
            unittest.main()
