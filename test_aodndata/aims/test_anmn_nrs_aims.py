from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.aims.anmn_nrs import AnmnNrsAimsHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_ANMN_Z_20170201T000000Z_NRSDAR_FV01.31e4cadf90ba8824645001ea07b74814.nc')


class TestAnmnNrsAimsHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = AnmnNrsAimsHandler
        super(TestAnmnNrsAimsHandler, self).setUp()

    def test_good_netcdf(self):
        handler = self.run_handler(GOOD_NC,
                                   include_regexes=['IMOS_ANMN_Z_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']}
                                   )

        self.assertEqual(len(handler.file_collection), 1)
        f = handler.file_collection[0]
        self.assertEqual(f.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f.name, os.path.basename(GOOD_NC))
        self.assertEqual(f.dest_path, os.path.join('IMOS/ANMN/NRS/REAL_TIME/NRSDAR/actual_depth@1.0m_channel_33098',
                                                   '2017/QAQC/IMOS_ANMN_Z_20170201T000000Z_NRSDAR_FV01.nc'))
        self.assertTrue(f.is_checked)
        self.assertTrue(f.is_stored)


if __name__ == '__main__':
    unittest.main()
