import os
import shutil
import unittest
from tempfile import mkdtemp

import xarray as xr
from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFile, PipelineFileCollection
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileNameError
from aodncore.pipeline.storage import get_storage_broker
from aodncore.testlib import make_test_file, HandlerTestCase
from aodndata.aodn_wave.handler import AodnWaveHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))

RT_MONTHLY_FILE = os.path.join(TEST_ROOT, 'DOT-WA_20220901_MANDURAH_RT_WAVE-PARAMETERS_monthly.nc')  # TIME =
# "2022-09-13 18", "2022-09-14" ;

RT_INCOMING_FILE_1 = os.path.join(TEST_ROOT, 'DOT-WA_20220913T180000Z_MANDURAH_RT_WAVE-PARAMETERS_END-20220914T000000Z.nc')
RT_INCOMING_FILE_1_MOD = os.path.join(TEST_ROOT,
                                      'DOT-WA_20220913T180000Z_MANDURAH_RT_WAVE-PARAMETERS_END-20220914T000000Z'
                                      '-MODIFIED-VALUES.nc')
RT_INCOMING_FILE_2 = os.path.join(TEST_ROOT, 'DOT-WA_20220929T120000Z_MANDURAH_RT_WAVE-PARAMETERS_END-20220929T120000Z.nc')
RT_INCOMING_FILE_3 = os.path.join(TEST_ROOT, 'DOT-WA_20220929T180000Z_MANDURAH_RT_WAVE-PARAMETERS_END'
                                             '-20220929T180000Z.nc')

INPUT_FILE_REGEX = '^DOT-WA_[0-9]{8}T[0-9]{6}Z_.*_RT_WAVE-PARAMETERS_END-[0-9]{8}T[0-9]{6}Z.nc$'
RT_MONTHLY_REGEX = '^DOT-WA_[0-9]{8}_.*_RT_WAVE-PARAMETERS_monthly.nc$'


class TestAodnWaveHandler(HandlerTestCase):

    def setUp(self):
        self.tempdir = mkdtemp()
        self.handler_class = AodnWaveHandler

        super(TestAodnWaveHandler, self).setUp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_dest_path(self):
        testfile = 'DOT-WA_20170601_CAPE-NATURALISTE_DM_WAVE-PARAMETERS_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'CAPE-NATURALISTE',
                             os.path.basename(testfile)))

        testfile = 'BOM_19980107_CAPE-SORELL_DM_WAVE-PARAMETERS_END-19981231.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Bureau_of_Meteorology',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'CAPE-SORELL',
                             os.path.basename(testfile)))

        testfile = 'BOM_19980107_CAPE-DU-COUEDIC_DM_WAVE-PARAMETERS_END-19981231.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Bureau_of_Meteorology',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'CAPE-DU-COUEDIC',
                             os.path.basename(testfile)))

        testfile = 'DES-QLD_19750918_MACKAY_DM_WAVE-PARAMETERS_END-20110210.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Environment_and_Science-Queensland',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'MACKAY',
                             os.path.basename(testfile)))

        testfile = 'DTA_20190531_CAMPBELL-ISLAND_DM_WAVE-PARAMETERS_END-20190531.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Defence_Technology_Agency-New_Zealand',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'CAMPBELL-ISLAND',
                             os.path.basename(testfile)))

        testfile = 'IMOS_NTP-WAVE_20200113_TORBAY_DM_WAVE-PARAMETERS_END-20200319.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'IMOS/NTP/Low_Cost_Wave_Buoy_Technology',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'TORBAY',
                             os.path.basename(testfile)))

        testfile = 'NSW-DPE_20200113_MAROUBRA_DM_WAVE-SPECTRA_END-20200319.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Planning_and_Environment-New_South_Wales',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-SPECTRA',
                             'MAROUBRA',
                             os.path.basename(testfile)))

        testfile = 'UWA_20210701_KING-GEORGE-SOUND_DM_WAVE-PARAMETERS_END-20210801.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'UWA',
                             'WAVE-BUOYS',
                             'DELAYED',
                             'WAVE-PARAMETERS',
                             'KING-GEORGE-SOUND',
                             os.path.basename(testfile)))

        testfile = 'IMOS_ANMN-DEEP-WATER-WAVES_20230530T003000Z_BRISBANE-OFFSHORE_RT_WAVE-PARAMETERS_20230530T013000Z.nc'
        make_test_file(testfile, {'site_name': 'BRISBANE-OFFSHORE'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'IMOS','ANMN','Deep_Water_Waves',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'BRISBANE-OFFSHORE',
                             '2023',
                             'IMOS_ANMN-DEEP-WATER-WAVES_20230530_BRISBANE-OFFSHORE_RT_WAVE-PARAMETERS_monthly.nc'))

        testfile = 'IMOS_ANMN-WAVE-BUOYS_20230530T003000Z_MARIA-ISLAND_RT_WAVE-PARAMETERS_20230530T013000Z.nc'
        make_test_file(testfile, {'site_name': 'MARIA-ISLAND'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'IMOS', 'ANMN', 'Wave_Buoys',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MARIA-ISLAND',
                             '2023',
                             'IMOS_ANMN-WAVE-BUOYS_20230530_MARIA-ISLAND_RT_WAVE-PARAMETERS_monthly.nc'))

        testfile = 'IMOS_COASTAL-WAVE-BUOYS_20241112T003000Z_CORAL-BAY_RT_WAVE-PARAMETERS_20241112T003000Z.nc'
        make_test_file(testfile, {'site_name': 'CORAL-BAY'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'IMOS', 'COASTAL-WAVE-BUOYS',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'CORAL-BAY',
                             '2024',
                             'IMOS_COASTAL-WAVE-BUOYS_20241112_CORAL-BAY_RT_WAVE-PARAMETERS_monthly.nc'))

    def test_publication_integral_parameter(self):
        testfile = 'DOT-WA_20170601_CAPE-NATURALISTE_DM_WAVE-PARAMETERS_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        handler = self.run_handler(testfile)

        nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(nc[0].is_harvested)
        self.assertTrue(nc[0].is_stored)

    def test_publication_spectra(self):
        testfile = 'DOT-WA_20170601_CAPE-NATURALISTE_DM_WAVE-SPECTRA_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Cape Naturaliste'},
                       WSSH={}
                       )
        handler = self.run_handler(testfile)

        nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(nc[0].publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertTrue(nc[0].is_stored)

    def test_publication_raw(self):
        testfile = 'DOT-WA_20170601_CAPE-NATURALISTE_DM_WAVE-RAW-DISPLACEMENTS_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Cape Naturaliste'},
                       WSSH={}
                       )
        handler = self.run_handler(testfile)

        nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        self.assertEqual(nc[0].publish_type, PipelineFilePublishType.UPLOAD_ONLY)
        self.assertTrue(nc[0].is_stored)

    def test_publication_bom_realtime_no_aggregation(self):
        """
        test processing of BOM WFS sourced NRT file : Case#1 incoming file is first file of the month as determined by
        the non-presence of a file in the destination path. File is simply renamed. Input file is archived
        """
        handler = self.run_handler(RT_INCOMING_FILE_1,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})
        monthly_nc = handler.file_collection.filter_by_attribute_regex('name',
                                                                       INPUT_FILE_REGEX)

        self.assertTrue(monthly_nc[0].is_stored)
        self.assertTrue(monthly_nc[0].is_harvested)
        self.assertTrue(monthly_nc[0].is_checked)

        destination = monthly_nc[0].dest_path
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             'DOT-WA_20220913_MANDURAH_RT_WAVE-PARAMETERS_monthly.nc'))
        # check file input file is archived and has original name
        archive_path = monthly_nc[0].archive_path
        self.assertTrue(monthly_nc[0].is_archived)
        self.assertEqual(archive_path,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             'DOT-WA_20220913T180000Z_MANDURAH_RT_WAVE-PARAMETERS_END-20220914T000000Z.nc'))

    def test_publication_bom_realtime_with_aggregation(self):
        """
            test processing of NRT file : Case#2 incoming file [T1; T2] needs to be aggregated with the existing monthly
            file [T0; T1].
            New monthly file will be generated by pipeline.
            """
        # create some PipelineFiles to represent the existing files on 'S3'

        preexisting_file = PipelineFileCollection()
        existing_file = PipelineFile(RT_MONTHLY_FILE, dest_path=os.path.join(
            'Department_of_Transport-Western_Australia', 'WAVE-BUOYS', 'REALTIME', 'WAVE-PARAMETERS',
            'MANDURAH', '2022', os.path.basename(RT_MONTHLY_FILE)))
        preexisting_file.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_file.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_file)

        handler = self.run_handler(RT_INCOMING_FILE_2,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})

        # check input file archived under original filename
        realtime_nc = handler.file_collection.filter_by_attribute_regex('name', INPUT_FILE_REGEX)
        self.assertEqual(os.path.join('Department_of_Transport-Western_Australia/WAVE-BUOYS/REALTIME/'
                                      'WAVE-PARAMETERS/MANDURAH/2022/'
                                      'DOT-WA_20220929T120000Z_MANDURAH_RT_WAVE-PARAMETERS_END-20220929T120000Z.nc'),
                         realtime_nc[0].archive_path)

        # check aggregated product (monthly file) harvested and pushed to S3
        monthly_nc = handler.file_collection.filter_by_attribute_regex('name',
                                                                       RT_MONTHLY_REGEX)
        self.assertEqual(monthly_nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(monthly_nc[0].is_stored)
        self.assertTrue(monthly_nc[0].is_harvested)
        self.assertTrue(monthly_nc[0].is_checked)

        destination = monthly_nc[0].dest_path
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             os.path.basename(RT_MONTHLY_FILE)))

    def test_publication_bom_realtime_with_aggregation_not_ordered(self):
        """
            test processing of NRT file : Case#3 incoming file needs to be aggregated with the existing monthly file.
            However, for some reason, such as the celery queue being restarted, the new file to aggregate doesn't have
            its timestamp right after the latest timestamp available in the monthly file but could well be in between
            the minimum and maximum timestamp of the existing monthly file
            New monthly file will be generated by pipeline
            """
        # create some PipelineFiles to represent the existing files on 'S3'

        preexisting_file = PipelineFileCollection()
        existing_file = PipelineFile(RT_MONTHLY_FILE, dest_path=os.path.join(
            'Department_of_Transport-Western_Australia', 'WAVE-BUOYS', 'REALTIME', 'WAVE-PARAMETERS',
            'MANDURAH', '2022', os.path.basename(RT_MONTHLY_FILE)))
        preexisting_file.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_file.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_file)

        handler = self.run_handler(RT_INCOMING_FILE_3,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})
        monthly_nc = handler.file_collection.filter_by_attribute_regex('name',
                                                                       RT_MONTHLY_REGEX)
        self.assertEqual(monthly_nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(monthly_nc[0].is_stored)
        self.assertTrue(monthly_nc[0].is_harvested)
        self.assertTrue(monthly_nc[0].is_checked)

        destination = monthly_nc[0].dest_path
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             os.path.basename(RT_MONTHLY_FILE)))

        # upload a new RT file which has its timestamp before the maximum timestamp of the monthly file available
        # What should happen in this scenario? discussion with @ggalibert on 2022/10/01: merge the data in a
        # monotonic fashion

        # TIME dimension has to be monotonic. However, this test is only tested in the IMOS checks,
        # not in the CF one as in 4.1.1

        handler = self.run_handler(RT_INCOMING_FILE_2,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})
        monthly_nc = handler.file_collection.filter_by_attribute_regex('name',
                                                                       RT_MONTHLY_REGEX)
        self.assertEqual(monthly_nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(monthly_nc[0].is_stored)
        self.assertTrue(monthly_nc[0].is_harvested)
        self.assertTrue(monthly_nc[0].is_checked)

        destination = monthly_nc[0].dest_path
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             os.path.basename(RT_MONTHLY_FILE)))

    def test_publication_bom_realtime_with_aggregation_not_strictly_monotonic(self):
        """
        test processing of NRT file : Case#4 incoming file [T0; T1] needs to be aggregated with the existing monthly
        file [T0; T1].
        New monthly file will be generated by pipeline. But in this case, TIME values aren't strictly monotonic and will
        be duplicates.
        We're handling two cases here:
        1) Rows where all values are duplicate will be deleted and the new files will be generated successfully
        2) Rows have similar timestamps, but some parameter values are different. This will raise an exception
        """
        # create some PipelineFiles to represent the existing files on 'S3'

        preexisting_file = PipelineFileCollection()
        existing_file = PipelineFile(RT_MONTHLY_FILE, dest_path=os.path.join(
            'Department_of_Transport-Western_Australia', 'WAVE-BUOYS', 'REALTIME', 'WAVE-PARAMETERS',
            'MANDURAH', '2022', os.path.basename(RT_MONTHLY_FILE)))
        preexisting_file.update([existing_file])

        # set the files to UPLOAD_ONLY
        preexisting_file.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # upload the 'preexisting_files' collection to the unit test's temporary upload location
        broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
        broker.upload(preexisting_file)

        # we process the case where the RT file has similar values to the existing monthly file. Everything should work
        # smoothly
        handler = self.run_handler(RT_INCOMING_FILE_1,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})
        monthly_nc = handler.file_collection.filter_by_attribute_regex('name',
                                                                       RT_MONTHLY_REGEX)
       # self.assertEqual(monthly_nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(monthly_nc[0].is_stored)
        self.assertTrue(monthly_nc[0].is_harvested)
        self.assertTrue(monthly_nc[0].is_checked)

        # check for non duplicate values to make sure aggregation code didn't change in a breakable manner
        with xr.open_dataset(os.path.join(broker.prefix, monthly_nc[0].dest_path), mode='r+') as ds:
            df = ds.to_dataframe()
            self.assertTrue(df.index.is_monotonic_increasing and df.index.is_unique)

        # the following is an exception because we're aggregating an RT files to an existing monthly file. The two files
        # have the same timestamps. The aggregation code will delete duplicate values, BUT their parameter values are
        # different. This raises an exception
        self.run_handler_with_exception(InvalidFileContentError, RT_INCOMING_FILE_1_MOD,
                                        check_params={'checks': ['cf:1.6'],
                                                      'criteria': 'lenient'})

    def test_publication_sofar_omc_realtime(self):
        """
        test processing of BOM WFS sourced NRT file : Case#1 incoming file is first file of the month as determined by the presence
        of a file in the destination path. File is simply renamed. Input file is published(harvest_upload)
        """

        testfile = 'NSW-DPE_20220901_BENGELLO_RT_WAVE-PARAMETERS_monthly.nc'
        make_test_file(testfile, {'site_name': 'Bengello'},
                       WSSH={}
                       )
        handler = self.run_handler(testfile,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})

        nc = handler.file_collection.filter_by_attribute_regex('name','^NSW-DPE.*_RT_WAVE-PARAMETERS_monthly.nc')
        #self.assertEqual(nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(nc[0].is_stored)
        self.assertTrue(nc[0].is_harvested)
        self.assertFalse(nc[0].is_archived)
        destination = nc[0].dest_path
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Planning_and_Environment-New_South_Wales',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'BENGELLO',
                             '2022',
                             os.path.basename(testfile)))


    def test_publication_monthly_BOM_file(self):
        """
        test case when need to repush a BOM monthly file through the pipeline
        """
        handler = self.run_handler(RT_MONTHLY_FILE,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})
        nc = handler.file_collection.filter_by_attribute_regex('name', RT_MONTHLY_REGEX)
        #self.assertEqual(nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        destination = nc[0].dest_path
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             os.path.basename(RT_MONTHLY_FILE)))

    def test_sitename_is_dash_separated(self):
        testfile = 'DOT-WA_20170601_CAPE_NATURALISTE_DM_WAVE-RAW-DISPLACEMENTS_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Cape Naturaliste'})
        with self.assertRaises(InvalidFileNameError):
            AodnWaveHandler.dest_path(testfile)

        testfile = 'IMOS_NTP_WAVE_20200113_CAPE_BRIDGEWATER_DM_WAVE-PARAMETERS_END-20200319.nc'
        make_test_file(testfile, {'site_name': 'Cape Bridgewater'})
        with self.assertRaises(InvalidFileNameError):
            AodnWaveHandler.dest_path(testfile)

    def test_mode_in_filename(self):
        testfile = 'UWA_20170601_TORBAY_WAVE-RAW-DISPLACEMENTS_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Torbay'})
        with self.assertRaises(InvalidFileNameError):
            AodnWaveHandler.dest_path(testfile)

    def test_rename_monthly_file(self):
        # First agregated product for a month is simply renamed
        mytestfile = 'NSW-DPE_20220901T000000Z_BENGELLO_RT_WAVE-PARAMETERS_monthly.nc'
        make_test_file(mytestfile, {'site_name': 'Bengello'})
        handler = self.run_handler(mytestfile,
                                   check_params={'checks': ['cf:1.6'],
                                                 'criteria': 'lenient'})
        nc = handler.file_collection.filter_by_attribute_regex('name','^NSW-DPE.*_RT_WAVE-PARAMETERS_monthly.nc')
        self.assertTrue(nc[0].is_stored)
        self.assertTrue(nc[0].is_harvested)
        self.assertEqual(os.path.basename(nc[0].dest_path),'NSW-DPE_20220901_BENGELLO_RT_WAVE-PARAMETERS_monthly.nc')

if __name__ == '__main__':
    unittest.main()