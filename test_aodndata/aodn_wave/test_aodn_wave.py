import os
import unittest
import shutil
from tempfile import mkdtemp

from aodncore.pipeline import FileType, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError, InvalidInputFileError
from aodncore.testlib import make_test_file, handlertest, HandlerTestCase
from aodndata.aodn_wave import handler
from aodndata.aodn_wave.handler import AodnWaveHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))

PARAMETERS_FILE = os.path.join(TEST_ROOT, 'NSW-DPE_20160811_MAROUBRA_DM_WAVE-PARAMETERS_END-20160912.nc')
SPECTRA_FILE = os.path.join(TEST_ROOT, 'WAVE-SPECTRA_END-12345678.nc')
RAWDISPL_FILE = os.path.join(TEST_ROOT, 'WAVE-RAW-DISPLACEMENTS_END-12345678.nc')


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

        testfile = 'BOM_19980107_CAPE-DU-COUEDIC_RT_WAVE-PARAMETERS_END-19981231.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Bureau_of_Meteorology',
                             'WAVE-BUOYS',
                             'REALTIME',
                             'WAVE-PARAMETERS',
                             'CAPE-DU-COUEDIC',
                             os.path.basename(testfile)))

        testfile = 'DES-QLD_19750918_MACKAY_RT_WAVE-PARAMETERS_END-20110210.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Environment_and_Science-Queensland',
                             'WAVE-BUOYS',
                             'REALTIME',
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


if __name__ == '__main__':
    unittest.main()
