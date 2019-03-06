import os

from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.testlib import HandlerTestCase

from aodndata.soop.soop_tmv_nrt import netcdf_writer, SoopTmvNrtHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
MOORING_LOG_10secs = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_DEV_20181102185130.log')
TRANSECT_LOG_10secs = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20181101090420.log')
TRANSECT_LOG_1sec = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20131006082240.log.1SecRaw.log')
BAD_LOG = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_DVE_20181102185130.log')
GOOD_ZIP = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20181101090420.log.zip')
GOOD_ZIP_WITH_META = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_D2M_20190302105320.zip')
DIFFERENT_TIME_FORMAT_LOG = os.path.join(TEST_ROOT, 'EPA_SOOP_TMV1_M2S_20180805220350.log')
ship_callsign_ls = {'VLST': 'Spirit-of-Tasmania-1'}


class TestSoopTmvNrtHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopTmvNrtHandler
        super(TestSoopTmvNrtHandler, self).setUp()

    def test_push_log_mooring_10secs(self):
        # test to push a 10secs mooring log file triggering the creation of a NetCDF

        handler = self.run_handler(MOORING_LOG_10secs,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/mooring/10secs/2018/'
                         'IMOS_SOOP-TMV_TSUB_20181102T185140Z_VLST_FV00_mooring-DEV_END-20181102T215350Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_log_transect_10secs(self):
        # test to push a 10secs transect log file triggering the creation of a NetCDF
        handler = self.run_handler(TRANSECT_LOG_10secs,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)

        f_nc = handler.file_collection[1]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/10secs/2018/'
                         'IMOS_SOOP-TMV_TSUB_20181101T090430Z_VLST_FV00_transect-D2M_END-20181101T184840Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_log_transect_1sec(self):
        # test to push a 1sec transect log file triggering the creation of a NetCDF
        handler = self.run_handler(TRANSECT_LOG_1sec,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/1sec/2013/'
                         'IMOS_SOOP-TMV_TSUB_20131006T082254Z_VLST_FV00_transect-D2M_END-20131006T190430Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_transect_netcdf(self):
        # test to push an already created NetCDF
        netcdf_path = netcdf_writer(TRANSECT_LOG_1sec, self.temp_dir, 'Spirit-of-Tasmania-1')
        handler = self.run_handler(netcdf_path,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/1sec/2013/'
                         'IMOS_SOOP-TMV_TSUB_20131006T082254Z_VLST_FV00_transect-D2M_END-20131006T190430Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_mooring_netcdf(self):
        # test to push an already created NetCDF
        netcdf_path = netcdf_writer(MOORING_LOG_10secs, self.temp_dir, 'Spirit-of-Tasmania-1')
        handler = self.run_handler(netcdf_path,
                                   check_params={'checks': ['cf', 'imos:1.4']},
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/mooring/10secs/2018/'
                         'IMOS_SOOP-TMV_TSUB_20181102T185140Z_VLST_FV00_mooring-DEV_END-20181102T215350Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_good_zip(self):

        handler = self.run_handler(GOOD_ZIP,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/10secs/2018/'
                         'IMOS_SOOP-TMV_TSUB_20181101T090430Z_VLST_FV00_transect-D2M_END-20181101T184840Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

        f_zip = handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP)[0]
        self.assertEqual(f_zip.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/10secs/2018/',
                                      os.path.basename(GOOD_ZIP)), f_zip.archive_path)

    def test_push_invalid_log(self):
        self.run_handler_with_exception(InvalidFileNameError, BAD_LOG,
                                        custom_params={'ship_callsign_ls': ship_callsign_ls})

    def test_push_log_different_time_format(self):
        # test to push a 10secs mooring log file triggering the creation of a NetCDF

        handler = self.run_handler(DIFFERENT_TIME_FORMAT_LOG,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/10secs/2018/'
                         'IMOS_SOOP-TMV_TSUB_20180805T220400Z_VLST_FV00_transect-M2S_END-20180806T212840Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

    def test_push_good_zip_with_meta(self):

        handler = self.run_handler(GOOD_ZIP_WITH_META,
                                   custom_params={'ship_callsign_ls': ship_callsign_ls})

        f_log = handler.file_collection.filter_by_attribute_value('extension', '.log')[0]
        self.assertEqual(f_log.publish_type, PipelineFilePublishType.NO_ACTION)

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/10secs/2019/'
                         'IMOS_SOOP-TMV_TSUB_20190302T105330Z_VLST_FV00_transect-D2M_END-20190302T202040Z.nc',
                         f_nc.dest_path)

        self.assertTrue(f_nc.is_checked)
        self.assertTrue(f_nc.is_stored)

        f_zip = handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP)[0]
        self.assertEqual(f_zip.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-TMV/VLST_Spirit-of-Tasmania-1/realtime/transect/10secs/2019/',
                                      os.path.basename(GOOD_ZIP_WITH_META)), f_zip.archive_path)
