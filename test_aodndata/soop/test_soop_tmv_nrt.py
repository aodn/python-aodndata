import os

from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodncore.testlib import HandlerTestCase

from aodndata.soop.soop_tmv_nrt import netcdf_writer, SoopTmvNrtHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
MOORING_LOG_10secs = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_DEV_20181102185130.log')
TRANSECT_LOG_10secs = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20181101090420.log')
TRANSECT_LOG_1sec = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20131006082240.log.1SecRaw.log')
BAD_LOG = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_DVE_20181102185130.log')
GOOD_10SECS_ZIP = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20181101090420.log.zip')
GOOD_10SECS_ZIP_WITH_META = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20190302105320.zip')
GOOD_1SEC_ZIP = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_DEV_20190222181410.log.1SecRaw.zip')
DIFFERENT_TIME_FORMAT_LOG = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_M2S_20180805220350.log')
MOORING_LOG_10SECS_WITH_COORD_GAP =os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_MEL_20141006052223.log')

ship_callsign_ls = {'VLST': 'Spirit-of-Tasmania-1'}
SOOP_TMV_NRT_DIR = 'IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/'


class TestSoopTmvNrtHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopTmvNrtHandler
        super(TestSoopTmvNrtHandler, self).setUp()

    def test_push_mooring_10secs_with_coordinate_gap_log(self):
        """ Test to push a 10secs mooring file log file missing coordinates at the start of the file. This is mainly to
        test we return the correct value of get_measurement_frequency
        NetCDF is NOT added to the collection
        log file is ARCHIVE_ONLY
        """
        handler = self.run_handler(MOORING_LOG_10SECS_WITH_COORD_GAP,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'mooring', '10secs', '2014', 'logs',
                                      os.path.basename(MOORING_LOG_10SECS_WITH_COORD_GAP)),
                         f_log.archive_path)

        # 10 secs NetCDF aren't added to the collection
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(0, len(f_nc))

    def test_push_mooring_10secs_log(self):
        """ Test to push a 10secs mooring log file triggering the creation of a NetCDF
        NetCDF file generated but NOT added to the collection
        log file is ARCHIVE_ONLY
        """

        handler = self.run_handler(MOORING_LOG_10secs,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(
            os.path.join(SOOP_TMV_NRT_DIR, 'mooring', '10secs', '2018', 'logs',
                         os.path.basename(MOORING_LOG_10secs)),
            f_log.archive_path)

        # 10 secs NetCDF aren't added to the collection
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(0, len(f_nc))

    def test_push_transect_10secs_log(self):
        """ Test to push a 10secs transect log file triggering the creation of a NetCDF
        NetCDF file generated but NOT added to the collection
        log file is ARCHIVE_ONLY
        """
        handler = self.run_handler(TRANSECT_LOG_10secs,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'transect', '10secs', '2018', 'logs',
                                      os.path.basename(TRANSECT_LOG_10secs)),
                         f_log.archive_path)

        # 10 secs NetCDF aren't added to the collection
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(0, len(f_nc))

    def test_push_transect_1sec_log(self):
        """ Test to push a 1sec transect log file triggering the creation of a NetCDF
        NetCDF is HARVEST_UPLOAD
        log file is UPLOAD_ONLY
        """
        handler = self.run_handler(TRANSECT_LOG_1sec,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'transect', '1sec', '2013', 'logs',
                                      os.path.basename(TRANSECT_LOG_1sec)),
                         f_log.dest_path)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(
            os.path.join(SOOP_TMV_NRT_DIR, 'transect/1sec/2013/',
                         'IMOS_SOOP-TMV_TSUB_20131006T082254Z_VLST_FV00_transect-D2M_END-20131006T190430Z.nc'),
            f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_transect_1sec_netcdf(self):
        """ Test to push an already created 1sec NetCDF
        NetCDF is HARVEST_UPLOAD
        """
        netcdf_path = netcdf_writer(TRANSECT_LOG_1sec, self.temp_dir, 'Spirit-of-Tasmania-1')
        handler = self.run_handler(netcdf_path,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(
            os.path.join(SOOP_TMV_NRT_DIR, 'transect/1sec/2013/'
                         'IMOS_SOOP-TMV_TSUB_20131006T082254Z_VLST_FV00_transect-D2M_END-20131006T190430Z.nc'),
            f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_mooring_10secs_netcdf(self):
        """ Test to push an already created 10secs NetCDF
        NetCDF lands to ERROR since it is a 10secs file. Only 1sec NetCDF are pushed to S3
        """
        netcdf_path = netcdf_writer(MOORING_LOG_10secs, self.temp_dir, 'Spirit-of-Tasmania-1')
        self.run_handler_with_exception(InvalidFileContentError,
                                        netcdf_path,
                                        custom_params={'ship_callsign_ls': ship_callsign_ls})

    def test_push_10secs_no_meta_zip(self):
        """ Test to push a 10secs zip file not containing a metadata txt file
        NetCDF generated but not added to the collection
        log is NO_ACTION
        zip is ARCHIVE_ONLY
        """
        handler = self.run_handler(GOOD_10SECS_ZIP,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)
        self.assertEqual(None, f_log.archive_path)

        # 10 secs NetCDF aren't added to the collection
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(0, len(f_nc))

        f_zip = handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP)[0]
        self.assertEqual(f_zip.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'transect', '10secs', '2018', 'logs',
                                      os.path.basename(GOOD_10SECS_ZIP)),
                         f_zip.archive_path)

    def test_push_good_10secs_with_meta_zip(self):
        """ Test to push a 10 secs zip file containing metadata text file
                NetCDF generated but not added to the collection
        log is NO_ACTION
        zip is ARCHIVE_ONLY
        """
        handler = self.run_handler(GOOD_10SECS_ZIP_WITH_META,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)
        self.assertEqual(None, f_log.archive_path)

        # 10 secs NetCDF aren't added to the collection
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(0, len(f_nc))

        f_zip = handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP)[0]
        self.assertEqual(f_zip.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'transect', '10secs', '2019', 'logs',
                                      os.path.basename(GOOD_10SECS_ZIP_WITH_META)),
                         f_zip.archive_path)

    def test_push_good_1sec_zip(self):
        """ Test to push a 1 sec zip file
        NetCDF is HARVEST_UPLOAD
        log is UPLOAD_ONLY
        zip is not added to the collection
        """
        handler = self.run_handler(GOOD_1SEC_ZIP,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'mooring', '1sec', '2019', 'logs',
                                      'EPA_SOOP_TMV1_DEV_20190222181410.log.1SecRaw.log'),
                         f_log.dest_path)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(
            os.path.join(SOOP_TMV_NRT_DIR, 'mooring', '1sec', '2019',
                         'IMOS_SOOP-TMV_TSUB_20190222T181411Z_VLST_FV00_mooring-DEV_END-20190222T220430Z.nc'),
            f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

        f_zip = handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP)
        self.assertEqual(0, len(f_zip))

    def test_push_invalid_log(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_LOG,
                                        custom_params={'ship_callsign_ls': ship_callsign_ls})

    def test_push_log_different_time_format(self):
        """ Test to push a 10secs mooring log file triggering the creation of a NetCDF
        """

        handler = self.run_handler(DIFFERENT_TIME_FORMAT_LOG,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join(SOOP_TMV_NRT_DIR, 'transect', '10secs', '2018', 'logs',
                                      os.path.basename(DIFFERENT_TIME_FORMAT_LOG)),
                         f_log.archive_path)

        # 10 secs NetCDF aren't added to the collection
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(0, len(f_nc))