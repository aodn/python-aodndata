from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from aodncore.testlib import HandlerTestCase
from aodndata.acorn.handler import AcornHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))

ACORN_RT_VARIOUS = {
    'IMOS_ACORN_V_20150301T013000Z_CBG_FV00_1-hour-avg.nc': 'IMOS/ACORN/gridded_1h-avg-current-map_non-QC/CBG/2015/03/01',
    'IMOS_ACORN_RV_20100530T220000Z_BFCV_FV00_radial.nc': 'IMOS/ACORN/radial/BFCV/2010/05/30',
    'IMOS_ACORN_RV_20110423T160000Z_CRVT_FV00_radial.nc': 'IMOS/ACORN/radial/CRVT/2011/04/23',
    'IMOS_ACORN_RV_20120316T200500Z_CSP_FV00_radial.nc': 'IMOS/ACORN/radial/CSP/2012/03/16',
    'IMOS_ACORN_RV_20130209T214000Z_CWI_FV00_radial.nc': 'IMOS/ACORN/radial/CWI/2013/02/09',
    'IMOS_ACORN_RV_20140102T035500Z_FRE_FV00_radial.nc': 'IMOS/ACORN/radial/FRE/2014/01/02',
    'IMOS_ACORN_RV_20151228T020000Z_GHED_FV00_radial.nc': 'IMOS/ACORN/radial/GHED/2015/12/28',
    'IMOS_ACORN_RV_20161121T003000Z_GUI_FV00_radial.nc':  'IMOS/ACORN/radial/GUI/2016/11/21',
    'IMOS_ACORN_RV_20171014T060000Z_LANC_FV00_radial.nc': 'IMOS/ACORN/radial/LANC/2017/10/14',
    'IMOS_ACORN_RV_20180907T210500Z_LEI_FV00_radial.nc': 'IMOS/ACORN/radial/LEI/2018/09/07',
    'IMOS_ACORN_RV_20190825T053500Z_NNB_FV00_radial.nc': 'IMOS/ACORN/radial/NNB/2019/08/25',
    'IMOS_ACORN_RV_20200718T140000Z_NOCR_FV00_radial.nc': 'IMOS/ACORN/radial/NOCR/2020/07/18',
    'IMOS_ACORN_RV_20210611T085000Z_RRK_FV00_radial.nc': 'IMOS/ACORN/radial/RRK/2021/06/11',
    'IMOS_ACORN_RV_20220504T010000Z_SBRD_FV00_radial.nc': 'IMOS/ACORN/radial/SBRD/2022/05/04',
    'IMOS_ACORN_RV_20230401T012000Z_TAN_FV00_radial.nc':'IMOS/ACORN/radial/TAN/2023/04/01',
    'IMOS_ACORN_V_20180910T010000Z_BONC_FV00_sea-state.nc': 'IMOS/ACORN/vector/BONC/2018/09/10',
    'IMOS_ACORN_V_20140804T010000Z_TURQ_FV00_sea-state.nc': 'IMOS/ACORN/vector/TURQ/2014/08/04',
}


class TestAcornRTHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AcornHandler
        super(TestAcornRTHandler, self).setUp()

    def test_various_path(self):
        for nc_file in ACORN_RT_VARIOUS.keys():
            dest_path = AcornHandler.dest_path(nc_file)
            self.assertEqual(dest_path, os.path.join(ACORN_RT_VARIOUS[nc_file], nc_file))


if __name__ == '__main__':
    unittest.main()
