import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileNameError

from aodndata.aodn_wave_dm.aodn_wave_dm import dest_path_aodn_wave_dm

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestAodnWaveDmHandler(unittest.TestCase):

    def test_dest_path_aodn_wave_dm(self):
        good_nc = os.path.join(TEST_ROOT, 'DOT-WA_T_20170601T043000Z_MAN02_AWAC-TEMP_FV01_END-20170918T070000Z.nc')
        self.assertEqual(dest_path_aodn_wave_dm(good_nc),
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'Acoustic_Wave-Current_Profiler',
                             'DELAYED',
                             'MAN02',
                             os.path.basename(good_nc)))

        good_nc = os.path.join(TEST_ROOT, 'DOT-WA_Z_20170601T050000Z_MAN02_AWAC-TIDE_FV01_END-20170918T070000Z.nc')
        self.assertEqual(dest_path_aodn_wave_dm(good_nc),
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'Acoustic_Wave-Current_Profiler',
                             'DELAYED',
                             'MAN02',
                             os.path.basename(good_nc)))

        good_nc = os.path.join(TEST_ROOT, 'BOM_W_19980107T042008Z_SORELL_WAVERIDER_FV01_END-19981231T133000Z.nc')
        self.assertEqual(dest_path_aodn_wave_dm(good_nc),
                         os.path.join(
                             'Bureau_of_Meteorology',
                             'Waverider_Buoys',
                             'DELAYED',
                             'Cape_Sorell',
                             os.path.basename(good_nc)))

        good_nc = os.path.join(TEST_ROOT, 'BOM_W_20001129T034756Z_COUEDIC_WAVERIDER_FV01_END-20001231T140424Z.nc')
        self.assertEqual(dest_path_aodn_wave_dm(good_nc),
                         os.path.join(
                             'Bureau_of_Meteorology',
                             'Waverider_Buoys',
                             'DELAYED',
                             'Cape_Du_Couedic',
                             os.path.basename(good_nc)))

        good_nc = os.path.join(TEST_ROOT, 'DOT-WA_W_20041231T163000Z_NAT46_WAVERIDER_FV01_END-20051231T150000Z.nc')
        self.assertEqual(dest_path_aodn_wave_dm(good_nc),
                         os.path.join(
                             'Department_of_Transport-Western_Australia',
                             'Waverider_Buoys',
                             'DELAYED',
                             'Cape_Naturaliste_02',
                             'NAT46',
                             os.path.basename(good_nc)))

        good_nc = os.path.join(TEST_ROOT, 'DES-QLD_W_19750918T170000Z_Mackay_WAVERIDER_FV01_END-20110210T133000Z.nc')
        self.assertEqual(dest_path_aodn_wave_dm(good_nc),
                         os.path.join(
                             'Department_of_Environment_and_Science-Queensland',
                             'Waverider_Buoys',
                             'DELAYED',
                             'Mackay',
                             os.path.basename(good_nc)))

        bad = os.path.join(TEST_ROOT, 'bad.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_aodn_wave_dm(bad)

        bad = os.path.join(TEST_ROOT, 'BOM_W_20001129T034756Z_UNKNOWN_WAVERIDER_FV01_END-20001231T140424Z.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_aodn_wave_dm(bad)


if __name__ == '__main__':
    unittest.main()