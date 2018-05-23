import os
import unittest

from shutil import copyfile
from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType, FileType
from aodncore.testlib import HandlerTestCase
from aodndata.anfog.handlers import AnfogHandler
from aodncore.util import extract_zip

TEST_ROOT = os.path.join(os.path.dirname(__file__))
TEST_MISSION_LIST = os.path.join(TEST_ROOT, 'HarvestmissionList.csv')
GOOD_NC = os.path.join(TEST_ROOT, 'IMOS_ANFOG_BCEOPSTUV_20180503T080042Z_SL210_FV01_timeseries_END-20180505T054942Z.nc')
GOOD_DSTG = os.path.join(TEST_ROOT, 'DSTO_MD_CEPSTUV_20130706T122916Z_SL090_FV01_timeseries_END-20130715T040955Z.nc')
GOOD_ZIP_DM = os.path.join(TEST_ROOT, 'BassStrait20160302.zip')
GOOD_ZIP_RT = os.path.join(TEST_ROOT, 'Forster20180205.zip')


class TestAnfogHandler(HandlerTestCase):
    """It is recommended to inherit from the HandlerTestCase class (which is itself a subclass of the standard
       unittest.TestCase class). This provides some useful methods and properties to shortcut some common test
       scenarios.
    """

    def setUp(self):
        # set the handler_class attribute to your handler (as imported above)
        self.handler_class = AnfogHandler

        # we copy the csv file usually in $WIP_DIR to the test temp folder
        self.temp_dir_mission_list = os.path.join(self.temp_dir, 'ANFOG', 'RT')
        os.makedirs(self.temp_dir_mission_list)

        # we copy the CSV to the temporary test folder
        self.harvest_mission_file = os.path.join(self.temp_dir_mission_list, 'HarvestmissionList.csv')
        copyfile(TEST_MISSION_LIST, os.path.join(self.temp_dir_mission_list, 'HarvestmissionList.csv'))

        # TODO -> cleaning temp files. Doesn't seem to be done when test fails

        super(TestAnfogHandler, self).setUp()

    def test_good_anfog_dm_file(self):

        handler = self.handler_class(GOOD_NC)
        handler.harvest_mission_file = self.harvest_mission_file  # we overwrite the class value for the unittest
        handler.check_params = {'checks': ['cf', 'imos:1.4']}
        handler.run()

        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)

        self.assertEqual(f.dest_path,
                         'IMOS/ANFOG/slocum_glider/TwoRocks20180503a/'
                         'IMOS_ANFOG_BCEOPSTUV_20180503T080042Z_SL210_FV01_timeseries_END-20180505T054942Z.nc')
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_good_anfog_dm_zip(self):

        handler = self.handler_class(GOOD_ZIP_DM)
        handler.harvest_mission_file = self.harvest_mission_file
        handler.check_params = {'checks': ['cf']}
        handler.run()

        raw = handler.file_collection.filter_by_attribute_value('extension', '.zip')
        jpg = handler.file_collection.filter_by_attribute_value('extension', '.jpg')

        nc_file = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        j = jpg[0]
        self.assertEqual(j.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertEqual(j.dest_path,
                         'IMOS/ANFOG/slocum_glider/BassStrait20160302/' + j.name)
        self.assertTrue(j.is_stored)

        r = raw[0]
        self.assertEqual(r.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(r.archive_path,
                         'IMOS/ANFOG/slocum_glider/BassStrait20160302/' + r.name)
        self.assertTrue(r.is_archived)
        for nc in nc_file:
            self.assertEqual(nc.dest_path,
                             'IMOS/ANFOG/slocum_glider/BassStrait20160302/' + nc.name)
            self.assertTrue(nc.is_stored)
            self.assertTrue(nc.is_checked)

    def test_good_anfog_rt_zip(self):

        handler = self.handler_class(GOOD_ZIP_RT)
        handler.harvest_mission_file = self.harvest_mission_file
        handler.run()

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
        handler = self.handler_class(GOOD_DSTG)
        handler.harvest_mission_file = self.harvest_mission_file
        handler.run()

        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         'Department_of_Defence/DSTG/slocum_glider/TalismanSaberB20130706/' + f.name)
        self.assertTrue(f.is_stored)

    def test_good_file_with_compliance_check(self):
        # we also expect this to succeed, since the test file is known be CF compliant
        handler = self.handler_class(GOOD_NC)
        handler.harvest_mission_file = self.harvest_mission_file
        handler.check_params = {'checks': ['cf', 'imos:1.4']}
        handler.run()

        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
