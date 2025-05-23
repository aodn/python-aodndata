import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileNameError

from aodndata.srs.srs_surface_waves import dest_path_srs_surface_waves, \
     dest_path_srs_surface_waves_sar

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSrsSurfaceWavesHandler(unittest.TestCase):

    def test_dest_path_srs_surface_waves_altimetry(self):
        good_nc_north = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_052N-000E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_north),
                         'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/040N_000E/{basename}'.format(
                             basename=os.path.basename(good_nc_north)),

        )

        good_nc_south = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_052S-043E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_south),
                         'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/060S_040E/{basename}'.format(
            basename=os.path.basename(good_nc_south)
        ))

        good_nc_0_south = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_002S-013E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_0_south),
                         'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/020S_000E/{basename}'.format(
            basename=os.path.basename(good_nc_0_south)
        ))

        good_nc_112_south = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_112S-013E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_112_south),
                         'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/120S_000E/{basename}'.format(
            basename=os.path.basename(good_nc_112_south)
        ))

        good_nc_122_south = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_122S-013E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_122_south),
                         'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/140S_000E/{basename}'.format(
            basename=os.path.basename(good_nc_122_south)
        ))

        bad_product = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_UNKNOWN-2_FV02_052S-000E-DM00.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_srs_surface_waves(bad_product)

    def test_dest_path_srs_surface_waves_scatterometry(self):
        good_nc = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_M_Wind-METOP-A_FV02_000N-180E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc),
                         'IMOS/SRS/Surface-Waves/Wind-Scatterometry-DM00/METOP-A/000N_180E/{basename}'.format(
            basename=os.path.basename(good_nc)
        ))

    def test_dest_path_srs_surface_waves_sar(self):
        good_nc_1b = os.path.join(TEST_ROOT,
                                     'IMOS_SRS-Surface-Waves_W_20190928T120118Z_Sentinel-1B_FV00_K2_END-20190929T105745Z.nc')
        self.assertEqual(dest_path_srs_surface_waves_sar(good_nc_1b),
                        'IMOS/SRS/Surface-Waves/SAR/REALTIME/SENTINEL-1B/2019/09/{basename}'.format(
           basename=os.path.basename(good_nc_1b)
        ))

        good_nc_1a = os.path.join(TEST_ROOT,
                                     'IMOS_SRS-Surface-Waves_W_20190928T151039Z_Sentinel-1A_FV00_K2_END-20190929T150836Z.nc')
        self.assertEqual(dest_path_srs_surface_waves_sar(good_nc_1a),
                         'IMOS/SRS/Surface-Waves/SAR/REALTIME/SENTINEL-1A/2019/09/{basename}'.format(
            basename=os.path.basename(good_nc_1a)
        ))

        good_nc_1a_qc = os.path.join(TEST_ROOT,
                                     'IMOS_SRS-Surface-Waves_W_20180426T063629Z_Sentinel-1A_FV01_DM00_K2_END-20180426T224953Z.nc')
        self.assertEqual(dest_path_srs_surface_waves_sar(good_nc_1a_qc),
                         'IMOS/SRS/Surface-Waves/SAR/DELAYED/SENTINEL-1A/2018/04/{basename}'.format(
            basename=os.path.basename(good_nc_1a_qc)
        ))

        bad = os.path.join(TEST_ROOT, 'BAD.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_srs_surface_waves_sar(bad)


if __name__ == '__main__':
    unittest.main()
