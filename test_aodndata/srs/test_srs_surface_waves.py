import os
import shutil
import unittest
from aodncore.testlib import HandlerTestCase

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodndata.srs.srs_surface_waves import SrsSurfaceWavesHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSrsSurfaceWavesHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsSurfaceWavesHandler
        super(TestSrsSurfaceWavesHandler, self).setUp()

    def test_dest_path_srs_surface_waves(self):
        good_nc_north = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_052N-000E-DM00.nc')
        self.assertEqual(SrsSurfaceWavesHandler.dest_path(good_nc_north), 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/{basename}'.format(
            basename=os.path.basename(good_nc_north)
        ))

        good_nc_south = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_052S-000E-DM00.nc')
        self.assertEqual(SrsSurfaceWavesHandler.dest_path(good_nc_south), 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/{basename}'.format(
            basename=os.path.basename(good_nc_south)
        ))

        bad_product = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_UNKNOWN-2_FV02_052S-000E-DM00.nc')
        with self.assertRaises(InvalidFileNameError):
            SrsSurfaceWavesHandler.dest_path(bad_product)

    def test_manifest_dir_srs_surface_waves(self):
        manifest_file = os.path.join(self.temp_dir, 'srs_surface_wave_1.dir_manifest')
        test_dir_path = os.path.join(self.temp_dir,
                                      'SRS/SURFACE_WAVE_PACK1/')
        shutil.copytree(os.path.join(TEST_ROOT, 'SURFACE_WAVE_PACK1/'),
                        os.path.join(self.temp_dir, 'SRS/SURFACE_WAVE_PACK1/'))

        with open(manifest_file, 'w') as f:
            f.write(test_dir_path)

        handler = self.handler_class(manifest_file)
        handler.relative_path_root = self.temp_dir
        handler.run()

        f = handler.file_collection[0]
        self.assertEqual(f.dest_path,
                         'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_036S-150E-DM00.nc')


if __name__ == '__main__':
    unittest.main()
