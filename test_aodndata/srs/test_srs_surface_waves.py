from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileNameError

from aodndata.srs.srs_surface_waves import dest_path_srs_surface_waves

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSrsSurfaceWavesHandler(unittest.TestCase):

    def test_dest_path_srs_surface_waves(self):
        good_nc_north = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_052N-000E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_north), 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/{basename}'.format(
            basename=os.path.basename(good_nc_north)
        ))

        good_nc_south = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_CRYOSAT-2_FV02_052S-000E-DM00.nc')
        self.assertEqual(dest_path_srs_surface_waves(good_nc_south), 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00/CRYOSAT-2/{basename}'.format(
            basename=os.path.basename(good_nc_south)
        ))

        bad_product = os.path.join(TEST_ROOT, 'IMOS_SRS-Surface-Waves_MW_UNKNOWN-2_FV02_052S-000E-DM00.nc')
        with self.assertRaises(InvalidFileNameError):
            dest_path_srs_surface_waves(bad_product)


if __name__ == '__main__':
    unittest.main()
