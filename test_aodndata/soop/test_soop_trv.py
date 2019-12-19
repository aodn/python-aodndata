import os
import unittest
from unittest.mock import patch

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodncore.util.wfs import WfsBroker

from aodndata.soop.soop_trv import SoopTrvHandler

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-TRV_B_20100225T073727Z_VMQ9273_FV01_END-20100225T131607Z_C-2016225T100000Z.nc')

TEST_DESCRIBEFEATURETYPE_RESPONSE = '''<?xml version="1.0" encoding="UTF-8"?><xsd:schema xmlns:gml="http://www.opengis.net/gml" xmlns:imos="imos.mod" xmlns:xsd="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified" targetNamespace="imos.mod">
  <xsd:import namespace="http://www.opengis.net/gml" schemaLocation="http://geoserver-123.aodn.org.au/geoserver/schemas/gml/2.1.2/feature.xsd"/>
  <xsd:complexType name="soop_trv_duplicate_urlType">
    <xsd:complexContent>
      <xsd:extension base="gml:AbstractFeatureType">
        <xsd:sequence>          
          <xsd:element maxOccurs="1" minOccurs="0" name="url" nillable="true" type="xsd:string"/>        
        </xsd:sequence>
      </xsd:extension>
    </xsd:complexContent>
  </xsd:complexType>
  <xsd:element name="soop_trv_duplicate_url" substitutionGroup="gml:_Feature" type="imos:soop_trv_duplicate_urlType"/>
</xsd:schema>
'''

TEST_GET_SCHEMA_RESPONSE = {"geometry": "GeometryCollection",
                            "properties": {"url": "string"},
                            "geometry_column": "geom"}

TEST_GETFEATURE_RESPONSE = '{"type":"FeatureCollection","totalFeatures":780,"features":[{"type":"Feature","id":"soop_trv_duplicate_url.fid-6f08f674_166ec2b1090_-67e1","geometry":null,"properties":{"url":"IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/temperature/IMOS_SOOP-TRV_T_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc"}},{"type":"Feature","id":"soop_trv_duplicate_url.fid-6f08f674_166ec2b1090_-67e0","geometry":null,"properties":{"url":"IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/salinity/IMOS_SOOP-TRV_S_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc"}}],"crs":null}'


class TestSoopTrvHandler(HandlerTestCase):
    def setUp(self):
        self.handler_class = SoopTrvHandler
        super(TestSoopTrvHandler, self).setUp()

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_good_netcdf(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.return_value = TEST_GETFEATURE_RESPONSE
        mock_webfeatureservice().get_schema.return_value = TEST_GET_SCHEMA_RESPONSE

        handler = self.run_handler(GOOD_NC,
                                   include_regexes=['IMOS_SOOP-TRV_B_.*\.nc'],
                                   check_params={'checks': ['cf', 'imos:1.3']}
                                   )

        self.assertEqual(len(handler.file_collection), 3)  # total number of files handled

        # section to test files to be deleted from WFS
        f_delete = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                  PipelineFilePublishType.DELETE_UNHARVEST)
        self.assertEqual(len(f_delete), 2)
        self.assertEqual(f_delete[0].dest_path,
                         'IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/temperature/IMOS_SOOP-TRV_T_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc')

        # section to test files to be uploaded
        f_upload = handler.file_collection.filter_by_attribute_id('publish_type',
                                                                  PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(len(f_upload), 1)

        f_good = f_upload[0]
        self.assertEqual(f_good.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)
        self.assertEqual(f_good.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(f_good.name, os.path.basename(GOOD_NC))
        self.assertEqual(f_good.dest_path,
                         'IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20100225T073727Z_END-20100225T131607Z/chlorophyll/IMOS_SOOP-TRV_B_20100225T073727Z_VMQ9273_FV01_END-20100225T131607Z.nc')
        self.assertTrue(f_good.is_checked)
        self.assertTrue(f_good.is_stored)

    @patch('aodncore.util.wfs.WebFeatureService')
    def test_delete_from_wfs(self, mock_webfeatureservice):
        mock_webfeatureservice().getfeature().getvalue.return_value = TEST_GETFEATURE_RESPONSE
        mock_webfeatureservice().get_schema.return_value = TEST_GET_SCHEMA_RESPONSE

        broker = WfsBroker(self.config.pipeline_config['global']['wfs_url'])

        files_for_layer = broker.query_urls_for_layer('soop_trv_duplicate_url')
        self.assertEqual(files_for_layer[0],
                         'IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/temperature/IMOS_SOOP-TRV_T_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc')


if __name__ == '__main__':
    unittest.main()
