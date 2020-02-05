import os
import unittest
from shutil import copyfile

from aodncore.testlib import HandlerTestCase
from aodndata.aatams.aatams_nrt import AatamsNrtHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT, 'IMOS_AATAMS-SATTAG_TSP_20090208T184000Z_Q9900180_FV00.nc')


class TestAatamsNrtHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AatamsNrtHandler
        super(TestAatamsNrtHandler, self).setUp()

    def test_rsync_manifest_file(self):
        MANIFEST_FILE = os.path.join(self._temp_dir, 'aatams_nrt.manifest')
        test_nc_path = os.path.join(self._temp_dir,
                                     'AATAMS/AATAMS_sattag_nrt/NETCDF/AATAMS/AATAMS_sattag_nrt/Q9900180/profiles')
        os.makedirs(test_nc_path)
        copyfile(GOOD_NC, os.path.join(test_nc_path, os.path.basename(GOOD_NC)))

        with open(MANIFEST_FILE, 'w') as f:
            f.write(os.path.join(test_nc_path, os.path.basename(GOOD_NC)))

        handler = self.run_handler(MANIFEST_FILE,
                                   include_regexes=[r'IMOS_AATAMS-SATTAG.*\.nc'],
                                   check_params={'checks': ['cf']}
                                   )
        f = handler.file_collection[0]
        self.assertEqual(f.dest_path, 'IMOS/AATAMS/AATAMS_sattag_nrt/Q9900180/profiles/IMOS_AATAMS-SATTAG_TSP_20090208T184000Z_Q9900180_FV00.nc')


if __name__ == '__main__':
    unittest.main()
