from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from aodndata.csiro.ocean_acidification import dest_path_oa

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestOaHandler(unittest.TestCase):

    def test_dest_path_oa(self):
        good_nc = os.path.join(TEST_ROOT, 'OA_Reconstruction.nc')
        self.assertEqual(dest_path_oa(good_nc), 'CSIRO/Climatology/Ocean_Acidification/OA_Reconstruction.nc')


if __name__ == '__main__':
    unittest.main()
