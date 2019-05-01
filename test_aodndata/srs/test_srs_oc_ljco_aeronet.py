import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileNameError

from aodndata.srs.srs_oc_ljco_aeronet import dest_path_srs_oc_ljco_aeronet

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSrsOcLjcoAeronet(unittest.TestCase):

    def test_dest_path_srs_surface_waves(self):
        good_nc = os.path.join(TEST_ROOT, 'Lucinda.lev20')
        self.assertEqual(dest_path_srs_oc_ljco_aeronet(good_nc),
                         'IMOS/SRS/OC/LJCO/AERONET/{basename}'.format(
                             basename=os.path.basename(good_nc)
                         ))

        bad_product = os.path.join(TEST_ROOT, 'BAD')
        with self.assertRaises(InvalidFileNameError):
            dest_path_srs_oc_ljco_aeronet(bad_product)


if __name__ == '__main__':
    unittest.main()
