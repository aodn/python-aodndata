import os
import unittest

from aodncore.testlib import HandlerTestCase
from aodndata.aatams import dest_path_aatams_sattag_qc_ctd
from aodncore.pipeline.exceptions import InvalidFileNameError

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'ct108-300-13_prof.nc')
BAD_NC = os.path.join(TEST_ROOT, 'ct108-300-13_prof_bad.nc')


class TestAatamsQcCTDHandler(HandlerTestCase):

    def test_destpath(self):
        self.assertEqual('IMOS/AATAMS/satellite_tagging/MEOP_QC_CTD/ct108/ct108-300-13_prof.nc',
                         dest_path_aatams_sattag_qc_ctd(GOOD_NC))

        with self.assertRaises(InvalidFileNameError):
            dest_path_aatams_sattag_qc_ctd(BAD_NC)


if __name__ == '__main__':
    unittest.main()
