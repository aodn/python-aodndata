import os
import unittest

from aodncore.pipeline import PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.testlib import HandlerTestCase

from aodndata.csiro.sstaars import SstaarsHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))


class TestSstaarsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SstaarsHandler
        super(TestSstaarsHandler, self).setUp()

    def test_dest_path_sstaars(self):
        good_nc = os.path.join(TEST_ROOT, 'SSTAARS.nc')
        self.assertEqual(SstaarsHandler.dest_path(good_nc), 'CSIRO/Climatology/SSTAARS/2017/SSTAARS.nc')

        good_nc_daily = os.path.join(TEST_ROOT, 'SSTAARS_daily_fit_001.nc')
        self.assertEqual(SstaarsHandler.dest_path(good_nc_daily), 'CSIRO/Climatology/SSTAARS/2017/AODN-product/SSTAARS_daily_fit_001.nc')

        good_nc_daily = os.path.join(TEST_ROOT, 'SSTAARS_daily_fit.nc')
        self.assertEqual(SstaarsHandler.dest_path(good_nc_daily),
                         'CSIRO/Climatology/SSTAARS/2017/AODN-product/SSTAARS_daily_fit.nc')

        bad_nc = os.path.join(TEST_ROOT, 'BAD.nc')
        with self.assertRaises(InvalidFileNameError):
            SstaarsHandler.dest_path(bad_nc)

    def test_publish_type(self):

        handler = self.run_handler(os.path.join(TEST_ROOT, 'SSTAARS.nc'))
        nc_file = handler.file_collection[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        handler = self.run_handler(os.path.join(TEST_ROOT, 'SSTAARS_daily_fit.nc'))
        nc_file = handler.file_collection[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.UPLOAD_ONLY)

        handler = self.run_handler(os.path.join(TEST_ROOT, 'SSTAARS_daily_fit_001.nc'))
        nc_file = handler.file_collection[0]
        self.assertEqual(nc_file.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)


if __name__ == '__main__':
    unittest.main()
