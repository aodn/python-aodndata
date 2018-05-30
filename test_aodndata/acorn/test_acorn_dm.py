import os
import unittest

from aodncore.testlib import HandlerTestCase
from aodndata.acorn.handler import AcornHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))

ACORN_DM_VARIOUS = {
    'IMOS_ACORN_RV_20120507T053500Z_CSP_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/CSP/2012/05/07',
    'IMOS_ACORN_RV_20130408T142000Z_CWI_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/CWI/2013/04/08',
    'IMOS_ACORN_RV_20140309T012500Z_FRE_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/FRE/2014/03/09',
    'IMOS_ACORN_RV_20150210T001000Z_GUI_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/GUI/2015/02/10',
    'IMOS_ACORN_RV_20160111T023500Z_LEI_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/LEI/2016/01/11',
    'IMOS_ACORN_RV_20171212T044500Z_NNB_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/NNB/2017/12/12',
    'IMOS_ACORN_RV_20181113T123000Z_RRK_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/RRK/2018/11/13',
    'IMOS_ACORN_RV_20191014T192000Z_TAN_FV01_radial.nc': 'IMOS/ACORN/radial_quality_controlled/TAN/2019/10/14',
    'IMOS_ACORN_W_20090808T023000Z_CBG_FV01_wavespec.nc': 'IMOS/ACORN/gridded_1h-avg-wave-spectra_QC/CBG/2009/08/08',
    'IMOS_ACORN_W_20090801T023000Z_CBG_FV01_wavespec.nc': 'IMOS/ACORN/gridded_1h-avg-wave-spectra_QC/CBG/2009/08/01',
    'IMOS_ACORN_MW_20110228T073000Z_CBG_FV01_windp.nc': 'IMOS/ACORN/gridded_1h-avg-wind-map_QC/CBG/2011/02/28',
    'IMOS_ACORN_MW_20110921T063000Z_SAG_FV01_windp.nc': 'IMOS/ACORN/gridded_1h-avg-wind-map_QC/SAG/2011/09/21',
    'IMOS_ACORN_W_20110921T053000Z_SAG_FV01_wavep.nc': 'IMOS/ACORN/gridded_1h-avg-wave-site-map_QC/SAG/2011/09/21',
    'IMOS_ACORN_W_20110921T053000Z_COF_FV01_wavep.nc': 'IMOS/ACORN/gridded_1h-avg-wave-site-map_QC/COF/2011/09/21',
    'IMOS_ACORN_W_20110921T053000Z_CSP_FV01_wavep.nc': 'IMOS/ACORN/gridded_1h-avg-wave-station-map_QC/CSP/2011/09/21'
}


class TestAcornDmHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AcornHandler
        super(TestAcornDmHandler, self).setUp()

    def test_various_path(self):
        for nc_file in ACORN_DM_VARIOUS.keys():
            dest_path = AcornHandler.dest_path(nc_file)
            self.assertEqual(dest_path, os.path.join(ACORN_DM_VARIOUS[nc_file], nc_file))


if __name__ == '__main__':
    unittest.main()
