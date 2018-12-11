from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.testlib import HandlerTestCase, mock

from aodndata.srs.srs_oc_soop_rad import SrsOcSoopRadHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
NC_FILE = os.path.join(TEST_ROOT,
                       'IMOS_SRS-OC_F_20180214T012503Z_VMQ9273_FV01_DALEC_END-20180214T054433Z.nc')

NC_FILE_FV02 = os.path.join(TEST_ROOT,
                       'IMOS_SRS-OC_F_20130730T010221Z_VMQ9273_FV02_DALEC_20130730T082813Z_C-20180522T055535Z.nc')

NC_FILE_CREATION_DATE = os.path.join(TEST_ROOT,
                                     'IMOS_SRS-OC_F_20180214T012503Z_VMQ9273_FV01_DALEC_END-20180214T054433Z_C-20180101T000000Z.nc')

NC_FILE_BAD_1 = os.path.join(TEST_ROOT,
                       'IMOS_SRS-OC_F_20180214T012503Z_UNKNOWNVESSEL_FV01_DALEC_END-20180214T054433Z.nc')

NC_FILE_BAD_2 = os.path.join(TEST_ROOT,
                       'IMOS_SRS-OC_F_20180214T012503Z_UNKNOWNVESSEL_FV01_UNKNOWNINSTRUMENT_END-20180214T054433Z.nc')

NC_FILE_BAD_3 = os.path.join(TEST_ROOT,
                       'BAD.nc')

def mock_ship_callsign_list():
    return {'VLHJ': 'Southern-Surveyor',
            'VMQ9273': 'Solander'}


class TestSrsOcSoopRadHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsOcSoopRadHandler
        super(TestSrsOcSoopRadHandler, self).setUp()

    @mock.patch("aodndata.srs.srs_oc_soop_rad.ship_callsign_list", side_effect=mock_ship_callsign_list)
    def test_good_netcdf(self, mock_ship):
        dest_path = SrsOcSoopRadHandler.dest_path(NC_FILE)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/OC/radiometer/VMQ9273_Solander/2018', os.path.basename(NC_FILE)))

        # same test as above but checking the creation date is stripped of the end
        dest_path = SrsOcSoopRadHandler.dest_path(NC_FILE_CREATION_DATE)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/OC/radiometer/VMQ9273_Solander/2018', os.path.basename(NC_FILE)))

        dest_path = SrsOcSoopRadHandler.dest_path(NC_FILE_FV02)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/OC/radiometer/VMQ9273_Solander/2013/fv02-products',
                                      'IMOS_SRS-OC_F_20130730T010221Z_VMQ9273_FV02_DALEC_20130730T082813Z.nc'))

    @mock.patch("aodndata.srs.srs_oc_soop_rad.ship_callsign_list", side_effect=mock_ship_callsign_list)
    def test_bad_netcdf(self, mock_ship):
        with self.assertRaises(InvalidFileNameError):
            SrsOcSoopRadHandler.dest_path(NC_FILE_BAD_1)

        with self.assertRaises(InvalidFileNameError):
            SrsOcSoopRadHandler.dest_path(NC_FILE_BAD_2)

        with self.assertRaises(InvalidFileNameError):
            SrsOcSoopRadHandler.dest_path(NC_FILE_BAD_3)


if __name__ == '__main__':
    unittest.main()
