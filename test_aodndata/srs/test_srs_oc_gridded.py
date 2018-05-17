import os

from aodncore.testlib import HandlerTestCase
from aodncore.pipeline.exceptions import InvalidFileNameError

from aodndata.srs.srs_oc_gridded import SrsOcGriddedHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))

SRS_S3_PREFIX = 'IMOS/SRS/OC/gridded'
SRS_VARIOUS = {'A.P1D.20151201T000000Z.aust.chl_gsm.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.chl_oc3.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.dt.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.ipar.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.K_490.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.l2_flags.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.nanop_brewin2010at.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.nanop_brewin2012in.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.npp_vgpm_eppley_gsm.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.npp_vgpm_eppley_oc3.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.owtd.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.par.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.picop_brewin2010at.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.picop_brewin2012in.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.sst.nc': 'aqua/P1D/2015/12',
               'A.P1D.20151201T000000Z.aust.tsm_clark16.nc': 'aqua/P1D/2015/12',
               'S.P1H.19981019T031100Z.overpass.chl_oc4.nc': 'seawifs/P1H/1998/10',
               'S.P1H.19981019T031100Z.overpass.npp_vgpm_eppley_oc4.nc': 'seawifs/P1H/1998/10',
               'S.P1H.19980119T031100Z.overpass.npp_vgpm_eppley_oc4.nc': 'seawifs/P1H/1998/01',
               'S.P1H.19981019T031100Z.overpass.tsm_clark.nc': 'seawifs/P1H/1998/10',
               'A20100322010059.L3m_MO_SO_Chl_9km.Johnson_SO_Chl.nc': 'contributed/SO-Johnson/chl/1m/aqua',
               'A20100322010059.L3m_8D_SO_Chl_9km.Johnson_SO_Chl.nc': 'contributed/SO-Johnson/chl/8d/aqua',
               'S20100322010059.L3m_MO_SO_Chl_9km.Johnson_SO_Chl.nc': 'contributed/SO-Johnson/chl/1m/seawifs',
               'S20100322010059.L3m_8D_SO_Chl_9km.Johnson_SO_Chl.nc': 'contributed/SO-Johnson/chl/8d/seawifs'
               }

SRS_BAD = {'bad.nc',
           'A.P1D.20151201T000000Z.aust.UNKOWN.nc'}


class TestSrsOcGriddedHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SrsOcGriddedHandler
        super(TestSrsOcGriddedHandler, self).setUp()

    def test_various_path(self):
        for nc_file in SRS_VARIOUS.keys():
            dest_path = SrsOcGriddedHandler.dest_path(nc_file)
            expected_path = os.path.join(SRS_S3_PREFIX, SRS_VARIOUS[nc_file], nc_file)
            self.assertEqual(dest_path, expected_path)

    def test_various_bad_path(self):
        for nc_file in SRS_BAD:
            with self.assertRaises(InvalidFileNameError):
                SrsOcGriddedHandler.dest_path(nc_file)
