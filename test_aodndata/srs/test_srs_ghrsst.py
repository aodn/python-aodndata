import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodncore.pipeline.exceptions import InvalidFileNameError

from aodndata.srs.srs_ghrsst import SrsGhrsstHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
SRS_L3S_1D_DAY = os.path.join(TEST_ROOT,
                              '19920326032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1d_day.nc')
SRS_L3S_1DS_DAY = '20170101111000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1d_dn_Southern.nc'
SRS_L3C_1D_DAY = '20170101032000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_day.nc'
SRS_L3U = '19940101052414-ABOM-L3U_GHRSST-SSTskin-AVHRR11_D-Asc.nc'
SRS_L3P = '20140101-ABOM-L3P_GHRSST-SSTsubskin-AVHRR_MOSAIC_01km-AO_DAAC.nc'
SRS_L3C_1DS_NGT = '20170101171000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_night_Southern.nc'
SRS_L4_RAMSSA = '20180502120000-ABOM-L4_GHRSST-SSTfnd-RAMSSA_09km-AUS-v02.0-fv01.0.nc'
SRS_L4_GAMSSA = '20180101120000-ABOM-L4_GHRSST-SSTfnd-GAMSSA_28km-GLOB-v02.0-fv01.0.nc'

SRS_VARIOUS = {'19950309232523-ABOM-L3U_GHRSST-SSTskin-AVHRR09_D-Des_Southern.nc': 'SRS/SST/ghrsst/L3U-S/n09/1995',
               '20151204200948-ABOM-L3U_GHRSST-SSTskin-AVHRR19_D-Des_Southern.nc': 'SRS/SST/ghrsst/L3U-S/n19/2015',
               '19950309232523-ABOM-L3U_GHRSST-SSTskin-AVHRR09_D-Des.nc': 'SRS/SST/ghrsst/L3U/n09/1995',
               '20151204200948-ABOM-L3U_GHRSST-SSTskin-AVHRR19_D-Des.nc': 'SRS/SST/ghrsst/L3U/n19/2015',
               '19950309232523-ABOM-L3U_GHRSST-SSTskin-AVHRR09_D-Asc.nc': 'SRS/SST/ghrsst/L3U/n09/1995',
               '20151204200948-ABOM-L3U_GHRSST-SSTskin-AVHRR19_D-Asc.nc': 'SRS/SST/ghrsst/L3U/n19/2015',
               '20151201152000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-6d_day.nc': 'SRS/SST/ghrsst/L3S-6d/day/2015',
               '20151201212000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-6d_dn.nc': 'SRS/SST/ghrsst/L3S-6d/dn/2015',
               '20151202032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-6d_night.nc': 'SRS/SST/ghrsst/L3S-6d/ngt/2015',
               '20151203152000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-3d_night.nc': 'SRS/SST/ghrsst/L3S-3d/ngt/2015',
               '20151203032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-3d_day.nc': 'SRS/SST/ghrsst/L3S-3d/day/2015',
               '20151203092000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-3d_dn.nc': 'SRS/SST/ghrsst/L3S-3d/dn/2015',
               '20151130231000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1m_dn_Southern.nc': 'SRS/SST/ghrsst/L3S-1mS/dn/2015',
               '20151130032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1m_night.nc': 'SRS/SST/ghrsst/L3S-1m/ngt/2015',
               '20150131092000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1m_dn.nc': 'SRS/SST/ghrsst/L3S-1m/dn/2015',
               '20151130152000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1m_day.nc': 'SRS/SST/ghrsst/L3S-1m/day/2015',
               '20151204111000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1d_dn_Southern.nc': 'SRS/SST/ghrsst/L3S-1dS/dn/2015',
               '20151204152000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1d_night.nc': 'SRS/SST/ghrsst/L3S-1d/ngt/2015',
               '20151204092000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1d_dn.nc': 'SRS/SST/ghrsst/L3S-1d/dn/2015',
               '20151204032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1d_day.nc': 'SRS/SST/ghrsst/L3S-1d/day/2015',
               '20151128032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-14d_night.nc': 'SRS/SST/ghrsst/L3S-14d/ngt/2015',
               '20151127212000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-14d_dn.nc': 'SRS/SST/ghrsst/L3S-14d/dn/2015',
               '20151127152000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-14d_day.nc': 'SRS/SST/ghrsst/L3S-14d/day/2015',
               '20151203152000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-3d_night.nc': 'SRS/SST/ghrsst/L3C-3d/ngt/n19/2015',
               '20151203032000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-3d_day.nc': 'SRS/SST/ghrsst/L3C-3d/day/n19/2015',
               '20151204171000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_night_Southern.nc': 'SRS/SST/ghrsst/L3C-1dS/ngt/n19/2015',
               '20151204051000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_day_Southern.nc': 'SRS/SST/ghrsst/L3C-1dS/day/n19/2015',
               '20151204152000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_night.nc': 'SRS/SST/ghrsst/L3C-1d/ngt/n19/2015',
               '20151204032000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_day.nc': 'SRS/SST/ghrsst/L3C-1d/day/n19/2015',
               '19990207111000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1d_dn_Southern.nc': 'SRS/SST/ghrsst/L3S-1dS/dn/1999',
               '20150623092000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1d_dn.nc': 'SRS/SST/ghrsst/L3S-1d/dn/2015',
               '20151203032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1d_day.nc': 'SRS/SST/ghrsst/L3S-1d/day/2015',
               '20151130152000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1d_night.nc': 'SRS/SST/ghrsst/L3S-1d/ngt/2015',
               '20151203032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-1d_dn.nc': 'SRS/SST/ghrsst/L3S-1d/dn/2015',
               '20151203032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-3d_dn.nc': 'SRS/SST/ghrsst/L3S-3d/dn/2015',
               '20151203032000-ABOM-L3S_GHRSST-SSTskin-AVHRR_D-6d_dn.nc': 'SRS/SST/ghrsst/L3S-6d/dn/2015',
               '19921231092000-ABOM-L3S_GHRSST-SSTfnd-AVHRR_D-1m_dn.nc': 'SRS/SST/ghrsst/L3S-1m/dn/1992',
               '20150722152000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-3d_night.nc': 'SRS/SST/ghrsst/L3C-3d/ngt/n19/2015',
               '20151130152000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-1d_night.nc': 'SRS/SST/ghrsst/L3C-1d/ngt/n19/2015',
               '20131011153743-ABOM-L3U_GHRSST-SSTskin-AVHRR19_D-Des_Southern.nc': 'SRS/SST/ghrsst/L3U-S/n19/2013',
               '20151201185911-ABOM-L3U_GHRSST-SSTskin-AVHRR19_D-Des.nc': 'SRS/SST/ghrsst/L3U/n19/2015',
               '20140428-ABOM-L3P_GHRSST-SSTsubskin-AVHRR_MOSAIC_01km-AO_DAAC.nc': 'SRS/SST/ghrsst/L3P/14d/2014',
               '20180612120000-ABOM-L4_GHRSST-SSTfnd-RAMSSA_09km-AUS-v02.0-fv01.0.nc': 'SRS/SST/ghrsst/L4/RAMSSA/2018',
               '20180613120000-ABOM-L4_GHRSST-SSTfnd-GAMSSA_28km-GLOB-v02.0-fv01.0.nc': 'SRS/SST/ghrsst/L4/GAMSSA/2018'

               }

SRS_BAD = {'19950309232523-ABOM-UNKNOWN_GHRSST-SSTskin-AVHRR09_D-Des_Southern.nc',
           '19950309232523-ABOM-L3U_GHRSST-SSTskin-AVHRR09_D-Des_South.nc',
           '20151130152000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-10d_night.nc',
           '20151130152000-ABOM-L3C_GHRSST-SSTskin-AVHRR19_D-10d_UNKNOWNDAYTIME.nc',
           '20131011153743-ABOM-L3U_GHRSST-SSTskin-AVHRR19_D-UNKNOWN_Southern.nc',
           'bad.nc'}


class TestSrsGhrsstHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsGhrsstHandler
        super(TestSrsGhrsstHandler, self).setUp()

    def test_l3s_netcdf(self):
        handler = self.run_handler(SRS_L3S_1D_DAY,
                                   check_params={'checks': ['cf', 'ghrsst:1.0']}
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.dest_path,
                         os.path.join('IMOS/SRS/SST/ghrsst/L3S-1d/day/1992', os.path.basename(SRS_L3S_1D_DAY)))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)

    def test_l3s_1ds_path(self):
        dest_path = SrsGhrsstHandler.dest_path(SRS_L3S_1DS_DAY)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/SST/ghrsst/L3S-1dS/dn/2017', os.path.basename(SRS_L3S_1DS_DAY)))

    def test_l3c_1d_path(self):
        # test with sat number in path
        dest_path = SrsGhrsstHandler.dest_path(SRS_L3C_1D_DAY)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/SST/ghrsst/L3C-1d/day/n19/2017', os.path.basename(SRS_L3C_1D_DAY)))

    def test_l3c_1ds_path(self):
        # test with sat number in path
        dest_path = SrsGhrsstHandler.dest_path(SRS_L3C_1DS_NGT)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/SST/ghrsst/L3C-1dS/ngt/n19/2017', os.path.basename(SRS_L3C_1DS_NGT)))

    def test_l3u_path(self):
        dest_path = SrsGhrsstHandler.dest_path(SRS_L3U)
        self.assertEqual(dest_path, os.path.join('IMOS/SRS/SST/ghrsst/L3U/n11/1994', os.path.basename(SRS_L3U)))

    def test_l3p_path(self):
        dest_path = SrsGhrsstHandler.dest_path(SRS_L3P)
        self.assertEqual(dest_path, os.path.join('IMOS/SRS/SST/ghrsst/L3P/14d/2014/', os.path.basename(SRS_L3P)))

    def test_l4_path(self):
        dest_path = SrsGhrsstHandler.dest_path(SRS_L4_RAMSSA)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/SST/ghrsst/L4/RAMSSA/2018/', os.path.basename(SRS_L4_RAMSSA)))

        dest_path = SrsGhrsstHandler.dest_path(SRS_L4_GAMSSA)
        self.assertEqual(dest_path,
                         os.path.join('IMOS/SRS/SST/ghrsst/L4/GAMSSA/2018/', os.path.basename(SRS_L4_GAMSSA)))

    def test_various_path(self):
        for nc_file in SRS_VARIOUS.keys():
            dest_path = SrsGhrsstHandler.dest_path(os.path.join(TEST_ROOT, nc_file))
            self.assertEqual(dest_path, os.path.join('IMOS', SRS_VARIOUS[nc_file], nc_file))

    def test_various_bad_path(self):
        for nc_file in SRS_BAD:
            with self.assertRaises(InvalidFileNameError):
                SrsGhrsstHandler.dest_path(os.path.join(TEST_ROOT, nc_file))


if __name__ == '__main__':
    unittest.main()
