import os
import unittest
import shutil
from tempfile import mkdtemp

from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodncore.testlib import make_test_file
from aodndata.aodn_wave.handler import AodnWaveHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestAodnWaveHandler(unittest.TestCase):

    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_dest_path(self):
        filename = 'NSW-DPE_20160811_MAROUBRA_DM_WAVE-PARAMETERS_END-20160912.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Planning_and_Environment-New_South_Wales',
                             'Wave_Buoys',
                             'Delayed',
                             'Wave-parameters',
                             'MAROUBRA',
                             os.path.basename(testfile)))

        testfile = 'DOT-WA_20170601_CAPE-NATURALISTE_DM_WAVE-PARAMETERS_END-20170918.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'Wave_Buoys',
                             'Delayed',
                             'Wave-parameters',
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
                             'Wave_Buoys',
                             'Delayed',
                             'Wave-parameters',
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
                             'Wave_Buoys',
                             'Realtime',
                             'Wave-parameters',
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
                             'Wave_Buoys',
                             'Realtime',
                             'Wave-parameters',
                             'MACKAY',
                             os.path.basename(testfile)))

        # testfile = 'IMOS_ANMN-NSW_20140529_BYRON_BAY_DM_WAVE-PARAMETERS_END-20151231.nc'
        # make_test_file(testfile, {'site_name': 'Maroubra'},
        #                WSSH={}
        #                )
        # dest_dir = AodnWaveHandler.dest_path(testfile)
        # self.assertEqual(dest_dir,
        #                  os.path.join(
        #                      'Department_of_Planning_and_Environment-New_South_Wales',
        #                      'Manly_Hydraulics_Laboratory',
        #                      'Wave_Buoys',
        #                      'Delayed',
        #                      'Wave-parameters',
        #                      'BYRON_BAY',
        #                      os.path.basename(testfile)))

        testfile = 'DTA_20190531_CAMPBELL-ISLAND_DM_WAVE-PARAMETERS_END-20190531.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Defence_Technology_Agency-New_Zealand',
                             'Wave_Buoys',
                             'Delayed',
                             'Wave-parameters',
                             'CAMPBELL-ISLAND',
                             os.path.basename(testfile)))

        testfile = 'DTA_20170530_SOUTHERN-OCEAN_DM_WAVE-PARAMETERS_END-20170530.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Defence_Technology_Agency-New_Zealand',
                             'Wave_Buoys',
                             'Delayed',
                             'Wave-parameters',
                             'SOUTHERN-OCEAN',
                             os.path.basename(testfile)))

        testfile = 'IMOS_NTP-WAVE_20200113_TORBAY_DM_WAVE-PARAMETERS_END-20200319.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'IMOS/NTP/Low_Cost_Wave_Buoy_Technology',
                             'Wave_Buoys',
                             'Delayed',
                             'Wave-parameters',
                             'TORBAY',
                             os.path.basename(testfile)))

        testfile = 'NSW-DPE_20200113_MAROUBRA_DM_SPECTRA_END-20200319.nc'
        make_test_file(testfile, {'site_name': 'Maroubra'},
                       WSSH={}
                       )
        dest_dir = AodnWaveHandler.dest_path(testfile)
        self.assertEqual(dest_dir,
                         os.path.join(
                             'Department_of_Planning_and_Environment-New_South_Wales',
                             'Wave_Buoys',
                             'Delayed',
                             'Spectra',
                             'MAROUBRA',
                             os.path.basename(testfile)))

    #   badmode = 'IMOS_NTP-WAVE_20200113_TORBAY_RM_WAVE-PARAMETERS_END-20200319.nc'
    #  with self.assertRaises(InvalidFileNameError):
    #     dest_path_aodn_wave_dm(badmode)


#     badplatform = 'BOM_W_20001129_CAMPBELL_WAVE-PARAMETERS_END-20001231.nc'
#     make_test_file(testfile, {'site_name': 'Maroubra'},
#                    WSSH={}
#                    )
#    dest_dir = dest_path_aodn_wave(badplatform)
#     with self.assertRaises(InvalidFileNameError):
#        dest_path_aodn_wave_dm(badplatform)


if __name__ == '__main__':
    unittest.main()
