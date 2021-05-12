import os
import unittest
import shutil

from aodncore.pipeline import PipelineFilePublishType, FileType
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileNameError
from aodncore.testlib import HandlerTestCase

from aodndata.moorings.handlers import DwmHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
IMAGES_ZIP_BASENAME = 'images_SAZ47-15-2012.zip'
IMAGES_ZIP = os.path.join(TEST_ROOT, IMAGES_ZIP_BASENAME)
IMAGES_ZIP_CONTENTS = {'saz_2012_47_1000_01.jpg', 'saz_2012_47_1000_02.JPG', 'saz_2012_47_1050_IRS_01.tiff'}
MIXED_ZIP = os.path.join(TEST_ROOT, 'images_and_nc.zip')
CALIBRATION_ZIP_BASENAME = 'calibration_Pulse-6-2009.zip'
CALIBRATION_ZIP = os.path.join(TEST_ROOT, CALIBRATION_ZIP_BASENAME)
CALIB_MIXED_ZIP = os.path.join(TEST_ROOT, 'calibration_and_nc.zip')

class TestDwmHandler(HandlerTestCase):
    """Tests DWM-specific behaviour only. The handling of NetCDF files is the same as
    in MooringsHandler, and is tested there.
    """

    def setUp(self):
        self.handler_class = DwmHandler
        super(TestDwmHandler, self).setUp()

    def test_images_zip(self):
        handler = self.run_handler(IMAGES_ZIP, include_regexes=['.*\\.(jpe?g|JPE?G|tiff?|TIFF?)'])

        self.assertEqual(4, len(handler.file_collection))

        images = handler.file_collection.filter_by_attribute_id_not('file_type', FileType.ZIP)
        self.assertSetEqual(IMAGES_ZIP_CONTENTS, set(images.get_attribute_list('name')))
        for f in images:
            self.assertIs(f.publish_type, PipelineFilePublishType.NO_ACTION)
            self.assertFalse(f.is_stored)

        for f in handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP):
            self.assertEqual(f.dest_path, os.path.join('IMOS', 'DWM', 'SOTS', 'images', IMAGES_ZIP_BASENAME))
            self.assertTrue(f.is_stored)
            self.assertTrue(f.is_harvested)

    def test_images_zip_good_names(self):
        for images_zip_name in ('images_SAZ46-19-2017.zip', 'images_OTHER-DEPLOYMENT-2021.zip'):
            images_zip = os.path.join(self.temp_dir, images_zip_name)
            shutil.copy(IMAGES_ZIP, images_zip)
            handler = self.run_handler(images_zip, include_regexes=['.*\\.(jpe?g|JPE?G|tiff?|TIFF?)'])
            self.assertEqual(4, len(handler.file_collection))
            self.assertTrue(handler.input_file_object.is_stored)
            self.assertTrue(handler.input_file_object.is_harvested)

    def test_images_zip_bad_names(self):
        for images_zip_name in ('NOT_matching_image_pattern.zip', 'SAZ47-15-2012-images.zip'):
            bad_images_zip = os.path.join(self.temp_dir, images_zip_name)
            shutil.copy(IMAGES_ZIP, bad_images_zip)
            handler = self.run_handler_with_exception(InvalidFileNameError, bad_images_zip)
            #self.assertRegex(handler.error.args[0], r"is an image or calibration zip file but has wrong name")

    def test_mixed_zip(self):
        self.run_handler_with_exception(InvalidFileContentError, MIXED_ZIP)

    def test_calib_zip(self):
        handler = self.run_handler(CALIBRATION_ZIP)
        self.assertTrue('calibration' in handler.file_basename)
        harvested_files = handler.file_collection.filter_by_bool_attribute('is_harvested')
        self.assertEqual(len(harvested_files), 1)
        self.assertIs(harvested_files[0].file_type, FileType.ZIP)

    def test_calib_zip_good_names(self):
        for calib_zip_name in ('calibration_Pulse-7-2007.zip', 'calibration_OTHER-8-2021.zip'):
            calib_zip = os.path.join(self.temp_dir, calib_zip_name)
            shutil.copy(CALIBRATION_ZIP, calib_zip)
            handler = self.run_handler(calib_zip)
            self.assertNotEqual(3, len(handler.file_collection))
            self.assertTrue(handler.input_file_object.is_stored)
            self.assertTrue(handler.input_file_object.is_harvested)

    def test_calib_zip_bad_names(self):
        for calib_zip_name in ('NOT_matching_calib_pattern.zip', 'Pulse-6-2009-calib.zip'):
            bad_calib_zip = os.path.join(self.temp_dir, calib_zip_name)
            shutil.copy(CALIBRATION_ZIP, bad_calib_zip)
            handler = self.run_handler_with_exception(InvalidFileNameError, bad_calib_zip)
            #self.assertRegex(handler.error.args[0], r"is an image or calibration zip file but has wrong name")

    def test_mixed_calib_zip(self):
        self.run_handler_with_exception(InvalidFileContentError, CALIB_MIXED_ZIP)


if __name__ == '__main__':
    unittest.main()