import os
import unittest
import shutil

from aodncore.pipeline import PipelineFilePublishType, FileType
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileNameError
from aodncore.testlib import HandlerTestCase

from aodndata.moorings.handlers import AbosHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
IMAGES_ZIP_BASENAME = 'images_SAZ47-15-2012.zip'
IMAGES_ZIP = os.path.join(TEST_ROOT, IMAGES_ZIP_BASENAME)
IMAGES_ZIP_CONTENTS = {'saz_2012_47_1000_01.jpg', 'saz_2012_47_1000_02.JPG', 'saz_2012_47_1050_IRS_01.tiff'}
MIXED_ZIP = os.path.join(TEST_ROOT, 'images_and_nc.zip')


class TestAbosHandler(HandlerTestCase):
    """Tests ABOS-specific behaviour only. The handling of NetCDF files is the same as
    in MooringsHandler, and is tested there.
    """

    def setUp(self):
        self.handler_class = AbosHandler
        super(TestAbosHandler, self).setUp()

    def test_images_zip(self):
        handler = self.run_handler(IMAGES_ZIP, include_regexes=['.*\\.(jpe?g|JPE?G|tiff?|TIFF?)'])

        self.assertEqual(4, len(handler.file_collection))

        images = handler.file_collection.filter_by_attribute_id_not('file_type', FileType.ZIP)
        self.assertSetEqual(IMAGES_ZIP_CONTENTS, set(images.get_attribute_list('name')))
        for f in images:
            self.assertIs(f.publish_type, PipelineFilePublishType.NO_ACTION)
            self.assertFalse(f.is_stored)

        for f in handler.file_collection.filter_by_attribute_id('file_type', FileType.ZIP):
            self.assertEqual(f.dest_path, os.path.join('IMOS', 'ABOS', 'SOTS', 'images', IMAGES_ZIP_BASENAME))
            self.assertTrue(f.is_stored)
            self.assertTrue(f.is_harvested)

    def test_bad_name_image_zip(self):
        bad_images_zip = os.path.join(self.temp_dir, 'NOT_matching_pattern.zip')
        shutil.copy(IMAGES_ZIP, bad_images_zip)
        handler = self.run_handler_with_exception(InvalidFileNameError, bad_images_zip,
                                                  include_regexes=['.*\\.(jpe?g|JPE?G|tiff?|TIFF?)'])
        self.assertRegex(handler.error.args[0], r"name does not match pattern for images zip file")

    def test_mixed_zip(self):
        self.run_handler_with_exception(InvalidFileContentError, MIXED_ZIP)


if __name__ == '__main__':
    unittest.main()
