import os
import unittest
import shutil
from tempfile import mkdtemp

from aodncore.pipeline import FileType, PipelineFilePublishType, PipelineFile, PipelineFileCollection
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError, InvalidInputFileError
from aodncore.testlib import make_test_file, HandlerTestCase
from aodndata.aodn_wave.handler import AodnWaveHandler
from aodncore.pipeline.storage import get_storage_broker

TEST_ROOT = os.path.join(os.path.dirname(__file__))

PARAMETERS_FILE = os.path.join(TEST_ROOT, 'NSW-DPE_20160811_MAROUBRA_DM_WAVE-PARAMETERS_END-20160912.nc')

RT_INCOMING_FILE = os.path.join(TEST_ROOT, 'DOT-WA_20220913T180000Z_MANDURAH_RT_WAVE-PARAMETERS_END-20220914T000000Z.nc')
RT_MONTHLY_FILE = os.path.join(TEST_ROOT, 'DOT-WA_20220901_MANDURAH_RT_WAVE-PARAMETERS_monthly.nc')
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
        test processing of BOM WFS sourced NRT file : Case#1 incoming file is first file of the month as determined by the presence
        of a file in the destination path. File is simply renamed. Input file is not published(no action)
        """
        handler = self.run_handler(RT_INCOMING_FILE)
        monthly_nc = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                    PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(monthly_nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(monthly_nc[0].is_stored)
        self.assertTrue(monthly_nc[0].is_harvested)

        destination = AodnWaveHandler.dest_path(os.path.basename(RT_MONTHLY_FILE))
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'MANDURAH',
                             '2022',
                             '09',
                            os.path.basename(RT_MONTHLY_FILE)))

        input_nc = handler.file_collection.filter_by_attribute_regex('name', INPUT_FILE_REGEX)
        self.assertEqual(input_nc[0].publish_type, PipelineFilePublishType.NO_ACTION)

    def test_publication_bom_realtime_with_aggregation(self):
            """
            test processing of NRT file : Case#2 incoming file needs to be aggregated with the existing monthly file.
            New monthly file will be generated by pipeline
            """
            # create some PipelineFiles to represent the existing files on 'S3'

            preexisting_file = PipelineFileCollection()
            existing_file = PipelineFile(RT_MONTHLY_FILE, dest_path=os.path.join(
                'Department_of_Transport-Western_Australia', 'WAVE-BUOYS', 'REALTIME', 'WAVE-PARAMETERS',
                'MANDURAH', '2022', '09', os.path.basename(RT_MONTHLY_FILE)))
            preexisting_file.update([existing_file])

            # set the files to UPLOAD_ONLY
            preexisting_file.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

            # upload the 'preexisting_files' collection to the unit test's temporary upload location
            broker = get_storage_broker(self.config.pipeline_config['global']['upload_uri'])
            broker.upload(preexisting_file)

            handler = self.run_handler(RT_INCOMING_FILE)
            monthly_nc = handler.file_collection.filter_by_attribute_regex('name',
                                                                        RT_MONTHLY_REGEX)
            self.assertEqual(monthly_nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
            self.assertTrue(monthly_nc[0].is_stored)
            self.assertTrue(monthly_nc[0].is_harvested)

            destination = AodnWaveHandler.dest_path(os.path.basename(RT_MONTHLY_FILE))
            self.assertEqual(destination,
                             os.path.join(
                                 'Department_of_Transport-Western_Australia',
                                 'WAVE-BUOYS',
                                 'REALTIME',
                                 'WAVE-PARAMETERS',
                                 'MANDURAH',
                                 '2022',
                                 '09',
                                 os.path.basename(RT_MONTHLY_FILE)))

    def test_publication_sofar_omc_realtime(self):
        """
        test processing of BOM WFS sourced NRT file : Case#1 incoming file is first file of the month as determined by the presence
        of a file in the destination path. File is simply renamed. Input file is not published(no action)
        """

        testfile = 'NSW-DPE_20220901T000000Z_BENGELLO_RT_WAVE-PARAMETERS_monthly.nc'
        make_test_file(testfile, {'site_name': 'Bengello'},
                       WSSH={}
                       )
        handler = self.run_handler(testfile)
        nc = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                    PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(nc[0].publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertTrue(nc[0].is_stored)
        self.assertTrue(nc[0].is_harvested)

        destination = AodnWaveHandler.dest_path(os.path.basename(testfile))
        self.assertEqual(destination,
                         os.path.join(
                             'Department_of_Planning_and_Environment-New_South_Wales',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'BENGELLO',
                             '2022',
                             '09',
                             os.path.basename(testfile)))

if __name__ == '__main__':
    unittest.main()
