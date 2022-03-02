#!/usr/bin/env python
"""Unit tests for DwmFileClassifier class"""

import os
import shutil
import unittest
from tempfile import mkdtemp

from aodncore.testlib import BaseTestCase, make_test_file
from aodndata.moorings.classifiers import DwmFileClassifier


class TestDwmFileClassifier(BaseTestCase):
    """Unit tests for DWM dest_path.py

    Test cases:
    * DA Temperature loggers
    * DA CTD_timeseries
    * DA Biogeochem_timeseries
    * DA Velocity (ADCP)
    * SOTS/SAZ CTD_timeseries
    * SOTS/SAZ Velocity
    * SOTS/SAZ Sediment_traps
    * SOTS sediment trap images
    * Pulse DM
    * Pulse RT
    * FluxPulse RT
    * SOFS DM
    * SOFS RT

    Other cases including missing attributes, etc... are already
    tested in test_file_classifier

    """

    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_da_temperature(self):
        filename = 'IMOS_DWM-DA_TZ_20120426T092000Z_EAC5_FV01_EAC5-2012-STARMON-MINI-300_END-20130826T222000Z_C' \
                   '-20140722T061401Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'platform_code': 'EAC5', 'featureType': 'timeSeries'},
                       TEMP={},
                       DEPTH={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/DA/EAC5/Temperature')
        self.assertEqual(dest_filename, filename)

    def test_da_ctd_timeseries(self):
        filename = 'IMOS_DWM-DA_STZ_20120426T092000Z_EAC5_FV01_EAC5-2012-SBE37SMP-202_END-20130826T222000Z_C' \
                   '-20140722T061531Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'platform_code': 'EAC5', 'featureType': 'timeSeries'},
                       TEMP={},
                       PSAL={},
                       PRES_REL={},
                       DEPTH={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/DA/EAC5/CTD_timeseries')
        self.assertEqual(dest_filename, filename)

    def test_sots_ctd_timeseries(self):
        filename = 'IMOS_DWM-SOTS_20120718T052204Z_SAZ_FV01_SAZ-15-microcat-4422m-2012_END-20131008T190000Z_C' \
                   '-20131216T221210Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'SOTS',
                                  'platform_code': 'SAZ47',
                                  'time_deployment_start': '2012-07-18T05:22:04Z',
                                  'time_coverage_start': '2012-07-18T05:22:04Z',
                                  'time_coverage_end': '2013-10-08T19:00:00Z'
                                  },
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2012')
        self.assertEqual(dest_filename, filename)

    def test_da_bgc_timeseries(self):
        filename = 'IMOS_DWM-DA_CEOSTZ_20140218T000057Z_TOTTEN1_FV01_TOTTEN1-SBE37SMP-ODO-9880_END' \
                   '-20150103T230035Z_C-20160112T020000Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'platform_code': 'TOTTEN1', 'featureType': 'timeSeries'},
                       TEMP={},
                       PRES={},
                       PSAL={},
                       CNDC={},
                       DOX1={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/DA/TOTTEN1/Biogeochem_timeseries')
        self.assertEqual(dest_filename, filename)

    def test_da_velocity(self):
        filename = 'IMOS_DWM-DA_AETVZ_20140204T000000Z_TOTTEN1_FV01_TOTTEN1-WORKHORSE-ADCP-14489_END' \
                   '-20150103T224000Z_C-20160112T020000Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'platform_code': 'TOTTEN1', 'featureType': 'timeSeries'},
                       UCUR={},
                       VCUR={},
                       WCUR={},
                       ECUR={},
                       CSPD={},
                       CDIR={},
                       TEMP={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/DA/TOTTEN1/Velocity')
        self.assertEqual(dest_filename, filename)

    def test_da_single_ping_velocity(self):
        filename = 'IMOS_DWM-DA_AETVZ_20190926T030000Z_EAC2000_FV00_EAC2000-2021-Long-Ranger-Workhorse-ADCP-120_END' \
                   '-20210527T213000Z_C-20211104T222150Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'platform_code': 'EAC2000'},
                       VEL1={'long_name': 'sea_water_velocity_from_acoustic_beam_1'},
                       VEL2={'long_name': 'sea_water_velocity_from_acoustic_beam_2'},
                       VEL3={'long_name': 'sea_water_velocity_from_acoustic_beam_3'},
                       ABSIC1={},
                       CMAG1={},
                       PERG1={},
                       TEMP={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/DA/EAC2000/Velocity/non-QC')
        self.assertEqual(dest_filename, filename)

    def test_sots_velocity(self):
        filename = 'IMOS_DWM-SOTS_AETVZ_20100912T224200Z_SAZ47_FV01_SAZ47-13-2010-Aquadopp-Current-Meter-1100_END' \
                   '-20110804T053000Z_C-20140826T062213Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'featureType': 'timeSeries',
                                  'site_code': 'SOTS',
                                  'platform_code': 'SAZ47',
                                  'time_deployment_start': '2010-09-12T22:42:00Z',
                                  'time_coverage_start': '2010-09-12T22:42:00Z',
                                  'time_coverage_end': '2011-08-04T05:30:00Z'
                                  },
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2010')
        self.assertEqual(dest_filename, filename)

    def test_sots_sediment_traps(self):
        filename = 'IMOS_DWM-SOTS_RFK_20120724T000000Z_SAZ47_FV01_SAZ47-2012Sediment-Trap-Data_20130828T000000Z_C' \
                   '-20150210T043901Z.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'featureType': 'timeSeries',
                                  'site_code': 'SOTS',
                                  'platform_code': 'SAZ47',
                                  'time_deployment_start': '2012-07-24T00:00:00Z',
                                  'time_coverage_start': '2012-07-24T00:00:00Z',
                                  'time_coverage_end': '2015-02-10T04:39:01Z'
                                  },
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2012')
        self.assertEqual(dest_filename, filename)

    def test_sots_images_zip(self):
        filename = 'images_SAZ47-15-2012.zip'
        testfile = os.path.join(self.tempdir, filename)
        dest_path = DwmFileClassifier.dest_path(testfile)
        self.assertEqual(os.path.join('IMOS/DWM/SOTS/images/', filename), dest_path)

        filename = 'images_SAZ47-17-2015.zip'
        testfile = os.path.join(self.tempdir, filename)
        dest_path = DwmFileClassifier.dest_path(testfile)
        self.assertEqual(os.path.join('IMOS/DWM/SOTS/images/', filename), dest_path)

    def test_sots_calibration_zip(self):
        filename = 'calibration_Pulse-6-2009.zip'
        testfile = os.path.join(self.tempdir, filename)
        dest_path = DwmFileClassifier.dest_path(testfile)
        self.assertEqual(os.path.join('IMOS/DWM/SOTS/calibration/', filename), dest_path)

        filename = 'calibration_SAZ47-17-2015.zip'
        testfile = os.path.join(self.tempdir, filename)
        dest_path = DwmFileClassifier.dest_path(testfile)
        self.assertEqual(os.path.join('IMOS/DWM/SOTS/calibration/', filename), dest_path)

    def test_pulse_delayed(self):
        filename = 'IMOS_DWM-SOTS_20130507T080000Z_Pulse_FV01_Pulse-10-2013_END-20131013T210000Z_C-20160315T000000Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'SOTS',
                                  'platform_code': 'Pulse',
                                  'time_deployment_start': '2013-05-07T08:00:00Z',
                                  'time_coverage_start': '2013-05-07T08:00:00Z',
                                  'time_coverage_end': '2013-10-13T21:00:00Z'
                                  }
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2013')
        self.assertEqual(dest_filename, filename)

    def test_pulse_realtime(self):
        filename = 'IMOS_DWM-SOTS_W_20150325T110000Z_Pulse_FV00_Pulse-11-2015-MRU-Surface-wave-height-realtime.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'SOTS',
                                  'platform_code': 'Pulse',
                                  'time_coverage_start': '2015-03-25T11:00:00Z'}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2015/real-time')
        self.assertEqual(dest_filename, filename)

    def test_fluxpulse_realtime(self):
        filename = 'IMOS_DWM-SOTS_W_20160316T140000Z_FluxPulse_FV00_FluxPulse-1-2016-MRU-Surface-wave-height.nc '
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'SOTS',
                                  'platform_code': 'FluxPulse',
                                  'data_mode': 'R',
                                  'time_coverage_start': '2016-03-16T14:00:00Z',
                                  'time_coverage_end': '2017-10-02T00:00:00Z'}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2016/real-time')
        self.assertEqual(dest_filename, filename)

    def test_sofs_surface_properties_dm(self):
        filename = \
            'IMOS_DWM-ASFS_RTSCP_20150101T000000Z_SOFS_FV00_SOFS-2014_END-20151212T000000Z_C-20140730T112324Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'time_deployment_start': '2014-12-25T12:00:00Z',
                                  'time_coverage_start': '2015-01-01T00:00:00Z',
                                  'time_coverage_end': '2015-12-12T00:00:00Z'},
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2014')
        self.assertEqual(dest_filename, filename)

    def test_sofs_waves_rt(self):
        filename = 'IMOS_DWM-SOTS_W_20190318_SOFS_FV00_SOFS-8-2019-MRU-Surface-wave-height-realtime.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile,
                       {'time_coverage_start': "2019-03-18T00:00:00Z",
                        'time_coverage_end': "2019-10-31T00:00:00Z"}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2019/real-time')
        self.assertEqual(dest_filename, filename)

    def test_sofs_oldnames_waves_rt(self):
        filename = 'IMOS_DWM-ASFS_W_20150202T000000Z_SOFS_FV01_TriAXYS.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile,
                       {'time_coverage_start': '2015-01-01T00:00:00Z',
                        'time_coverage_end': '2015-01-01T23:30:00Z'},
                       HAV={},
                       HMAX={},
                       HSIG={},
                       TSIG={},
                       VDIR={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/ASFS/SOFS/Surface_waves/Real-time/2015_daily')
        self.assertEqual(dest_filename, filename)

    @unittest.skip("not implemented yet - no files so far")
    def test_sofs_surface_properties_rt(self):
        assert(False)

    def test_sofs_oldnames_surface_properties_rt(self):
        filename = 'IMOS_DWM-ASFS_CMST_20150101T000000Z_SOFS_FV01_C-20160203T002503Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'time_coverage_start': '2015-01-01T00:00:00Z',
                                  'time_coverage_end': '2015-01-01T23:30:00Z'},
                       TEMP={},
                       PSAL={},
                       AIRT={},
                       RAIN_AMOUNT={},
                       RELH={},
                       WSPD={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/ASFS/SOFS/Surface_properties/Real-time/2015_daily')
        self.assertEqual(dest_filename, filename)

    @unittest.skip("not implemented yet - no files so far")
    def test_sofs_surface_fluxes_rt(self):
        assert(False)

    def test_sofs_oldnames_surface_fluxes_rt(self):
        filename = 'IMOS_DWM-ASFS_FMT_20150101T000000Z_SOFS_FV02.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile,
                       {'time_coverage_start': '2015-01-01T00:00:00Z',
                        'time_coverage_end': '2015-01-01T23:30:00Z'},
                       TEMP={},
                       PSAL={},
                       AIRT={},
                       HEAT_NET={},
                       MASS_NET={}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/ASFS/SOFS/Surface_fluxes/Real-time/2015_daily')
        self.assertEqual(dest_filename, filename)


    def test_sofs_one_day_delayed(self):
        filename = 'IMOS_DWM-ASFS_CMST_20150101T000000Z_SOFS_FV02_C-20171002T000000Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'data_mode': 'D',
                                  'time_coverage_start': '2015-01-01T00:00:00Z',
                                  'time_coverage_end': '2015-01-01T23:30:00Z'}
                       )
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/SOTS/2015')
        self.assertEqual(dest_filename, filename)

    def test_daily_depth_gridded_product(self):
        filename = 'IMOS_DWM-DA_STZV_20120401_EAC2000_FV02_daily-depth-gridded-product_END-20190924_C-20210910.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'EAC2000', 'featureType': 'timeSeriesProfile'}, TIME={}, DEPTH={}, TEMP={}, PSAL={}, UCUR={}, VCUR={})
        dest_dir, dest_filename = os.path.split(DwmFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/DWM/DA/CSIRO_gridded_all_variables')
        self.assertEqual(dest_filename, filename)

if __name__ == '__main__':
    unittest.main()
