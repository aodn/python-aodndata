from __future__ import absolute_import
from __future__ import unicode_literals
import unittest
import os

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodndata.aims.faimms import FaimmsHandler
from aodncore.testlib import HandlerTestCase

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_FAIMMS_T_20170101T000000Z_HIRP4_FV01.31e4cadf90ba8824645001ea07b74814.nc')


class TestFaimmsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = FaimmsHandler
        super(TestFaimmsHandler, self).setUp()

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                   include_regexes=['IMOS_FAIMMS_T_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']}
                                   )
        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path, os.path.join('IMOS/FAIMMS/Heron_Island/Relay_Pole_4',
                                                   'sea_water_temperature@1.8m_channel_25/2017/QAQC',
                                                   'IMOS_FAIMMS_T_20170101T000000Z_HIRP4_FV01.nc'))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
