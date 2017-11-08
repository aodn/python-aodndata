import os
import shutil
import unittest
from shutil import copyfile

from aodncore.testlib import HandlerTestCase
from aodndata.auv.handler import AuvHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
THUMBNAIL = os.path.join(TEST_ROOT, 'PR_20170526_080852_065_LC16.jpg')
CSV_PRODUCT = os.path.join(TEST_ROOT, 'DATA_WA201705_r20170526_080319_SS14_geebank_36m_out.csv')
NETCDF_B = os.path.join(TEST_ROOT, 'IMOS_AUV_B_20170526T080325Z_SIRIUS_FV00.nc')


class TestAuvHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AuvHandler
        super(TestAuvHandler, self).setUp()

    # test the different manifest files landing in the AUV incoming directory.
    def test_images_manifest_file(self):
        manifest_file = os.path.join(self.temp_dir,
                                     'WA201705-r20170526_080319_SS14_geebank_36m_out.images.manifest')
        test_thumb_path = os.path.join(self.temp_dir,
                                       'AUV/AUV_VIEWER_PROCESSING/thumbnails/WA201705/r20170526_080319_SS14_geebank_36m_out/thumbnails/')
        os.makedirs(test_thumb_path)
        copyfile(THUMBNAIL, os.path.join(test_thumb_path, os.path.basename(THUMBNAIL)))

        with open(manifest_file, 'w') as f:
            f.write(os.path.join(test_thumb_path, os.path.basename(THUMBNAIL)))

        handler = self.run_handler(manifest_file)
        f = handler.file_collection[0]

        self.assertEqual(f.dest_path, os.path.join(
            'IMOS/AUV/auv_viewer_data/images/WA201705/r20170526_080319_SS14_geebank_36m_out/thumbnails',
            os.path.basename(THUMBNAIL)))

    def test_csv_product_manifest_file(self):
        manifest_file = os.path.join(self.temp_dir, 'WA201705-r20170526_080319_SS14_geebank_36m_out.csv.manifest')
        test_csv_path = os.path.join(self.temp_dir, 'AUV/AUV_VIEWER_PROCESSING/WA201705')
        os.makedirs(test_csv_path)
        copyfile(CSV_PRODUCT, os.path.join(test_csv_path, os.path.basename(CSV_PRODUCT)))

        with open(manifest_file, 'w') as f:
            f.write(os.path.join(test_csv_path, os.path.basename(CSV_PRODUCT)))

        handler = self.run_handler(manifest_file)
        f = handler.file_collection[0]

        self.assertEqual(f.dest_path, os.path.join('IMOS/AUV/auv_viewer_data/csv_outputs/WA201705',
                                                   os.path.basename(CSV_PRODUCT)))

    def test_netcdf_product_manifest_file(self):
        manifest_file = os.path.join(self.temp_dir, 'WA201705-r20170526_080319_SS14_geebank_36m_out.netcdf.manifest')
        test_netcdf_path = os.path.join(self.temp_dir,
                                        'AUV/AUV_DOWNLOAD_CAMPAIGN/WA201705/r20170526_080319_SS14_geebank_36m_out/hydro_netcdf')
        os.makedirs(test_netcdf_path)
        copyfile(NETCDF_B, os.path.join(test_netcdf_path, os.path.basename(NETCDF_B)))

        with open(manifest_file, 'w') as f:
            f.write(os.path.join(test_netcdf_path, os.path.basename(NETCDF_B)))

        handler = self.run_handler(manifest_file,
                                   include_regexes=['IMOS_AUV_B_.*\.nc']
                                   )
        f = handler.file_collection[0]

        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/AUV/WA201705/r20170526_080319_SS14_geebank_36m_out/hydro_netcdf',
                                      os.path.basename(NETCDF_B)))

    def test_pdf_dir_manifest_file(self):
        manifest_file = os.path.join(self.temp_dir,
                                     'WA201705-r20170526_080319_SS14_geebank_36m_out.pdfreports.dir_manifest')
        test_report_path = os.path.join(self.temp_dir, 'AUV/AUV_DOWNLOAD_CAMPAIGN/WA201705/all_reports')
        shutil.copytree(os.path.join(TEST_ROOT, 'WA201705'),
                        os.path.join(self.temp_dir, 'AUV/AUV_DOWNLOAD_CAMPAIGN/WA201705'))

        with open(manifest_file, 'w') as f:
            f.write(test_report_path)

        handler = self.handler_class(manifest_file, include_regexes=['.*\.pdf'])
        handler.relative_path_root = self.temp_dir
        handler.run()

        f = handler.file_collection[0]
        self.assertEqual(f.dest_path, 'IMOS/AUV/WA201705/all_reports/r20170526_080319_SS14_geebank_36m_out_report.pdf')

    def test_dive_dir_manifest_file(self):
        manifest_file = os.path.join(self.temp_dir, 'WA201705-r20170526_080319_SS14_geebank_36m_out.dive.dir_manifest')
        test_dive_path = os.path.join(self.temp_dir,
                                      'AUV/AUV_DOWNLOAD_CAMPAIGN/WA201705/r20170526_080319_SS14_geebank_36m_out')
        shutil.copytree(os.path.join(TEST_ROOT, 'WA201705'),
                        os.path.join(self.temp_dir, 'AUV/AUV_DOWNLOAD_CAMPAIGN/WA201705'))

        with open(manifest_file, 'w') as f:
            f.write(test_dive_path)

        handler = self.handler_class(manifest_file)
        handler.relative_path_root = self.temp_dir
        handler.run()

        f = handler.file_collection[0]
        self.assertEqual(f.dest_path,
                         'IMOS/AUV/WA201705/r20170526_080319_SS14_geebank_36m_out/mosaic/image_r0004_c0056_rs0112_cs0112.tif')


if __name__ == '__main__':
    unittest.main()
