import os
import httpretty
import unittest

from aodncore.pipeline import PipelineFileCheckType, PipelineFilePublishType
from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_trv import SoopTrvHandler
from aodncore.util.wfs import WfsBroker
from aodncore.util import IndexedSet

TEST_ROOT = os.path.join(os.path.dirname(__file__))
GOOD_NC = os.path.join(TEST_ROOT,
                       'IMOS_SOOP-TRV_B_20100225T073727Z_VMQ9273_FV01_END-20100225T131607Z_C-2016225T100000Z.nc')

TEST_GETCAPABILITIES_RESPONSE = httpretty.Response('''<?xml version="1.0" encoding="UTF-8"?>
<WFS_Capabilities version="1.0.0" xmlns="http://www.opengis.net/wfs" xmlns:aodn="aodn" xmlns:imos="imos.mod" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wfs http://geoserver.example.com/geoserver/schemas/wfs/1.0.0/WFS-capabilities.xsd">
  <Service>
    <Name>WFS</Name>
    <Title />
    <Abstract />
    <Keywords />
    <OnlineResource>http://geoserver.example.com/geoserver/wfs</OnlineResource>
    <Fees />
    <AccessConstraints />
  </Service>
  <Capability>
    <Request>
      <GetCapabilities>
        <DCPType>
          <HTTP>
            <Get onlineResource="http://geoserver.example.com/geoserver/wfs?request=GetCapabilities" />
          </HTTP>
        </DCPType>
        <DCPType>
          <HTTP>
            <Post onlineResource="http://geoserver.example.com/geoserver/wfs" />
          </HTTP>
        </DCPType>
      </GetCapabilities>
      <DescribeFeatureType>
        <SchemaDescriptionLanguage>
          <XMLSCHEMA />
        </SchemaDescriptionLanguage>
        <DCPType>
          <HTTP>
            <Get onlineResource="http://geoserver.example.com/geoserver/wfs?request=DescribeFeatureType" />
          </HTTP>
        </DCPType>
        <DCPType>
          <HTTP>
            <Post onlineResource="http://geoserver.example.com/geoserver/wfs" />
          </HTTP>
        </DCPType>
      </DescribeFeatureType>
      <GetFeature>
        <ResultFormat>
          <CSV />
          <KML />
          <GML2 />
          <GML3 />
          <SHAPE-ZIP />
          <JSON />
        </ResultFormat>
        <DCPType>
          <HTTP>
            <Get onlineResource="http://geoserver.example.com/geoserver/wfs?request=GetFeature" />
          </HTTP>
        </DCPType>
        <DCPType>
          <HTTP>
            <Post onlineResource="http://geoserver.example.com/geoserver/wfs" />
          </HTTP>
        </DCPType>
      </GetFeature>
      <Transaction>
        <DCPType>
          <HTTP>
            <Get onlineResource="http://geoserver.example.com/geoserver/wfs?request=Transaction" />
          </HTTP>
        </DCPType>
        <DCPType>
          <HTTP>
            <Post onlineResource="http://geoserver.example.com/geoserver/wfs" />
          </HTTP>
        </DCPType>
      </Transaction>
      <LockFeature>
        <DCPType>
          <HTTP>
            <Get onlineResource="http://geoserver.example.com/geoserver/wfs?request=LockFeature" />
          </HTTP>
        </DCPType>
        <DCPType>
          <HTTP>
            <Post onlineResource="http://geoserver.example.com/geoserver/wfs" />
          </HTTP>
        </DCPType>
      </LockFeature>
      <GetFeatureWithLock>
        <ResultFormat>
          <GML2 />
        </ResultFormat>
        <DCPType>
          <HTTP>
            <Get onlineResource="http://geoserver.example.com/geoserver/wfs?request=GetFeatureWithLock" />
          </HTTP>
        </DCPType>
        <DCPType>
          <HTTP>
            <Post onlineResource="http://geoserver.example.com/geoserver/wfs" />
          </HTTP>
        </DCPType>
      </GetFeatureWithLock>
    </Request>
  </Capability>
  <FeatureTypeList>
    <Operations>
      <Query />
      <Insert />
      <Update />
      <Delete />
      <Lock />
    </Operations>
    <FeatureType>
      <Name>imos:soop_trv_duplicate_url</Name>
      <Title>soop trv duplicates</Title>
      <Abstract>soop trv duplicates.</Abstract>
      <Keywords>soop_trv_duplicate_url, features</Keywords>
      <SRS>EPSG:4326</SRS>
      <LatLongBoundingBox minx="-180.0" miny="-90.0" maxx="180.0" maxy="90.0" />
    </FeatureType>
  </FeatureTypeList>
  <ogc:Filter_Capabilities>
    <ogc:Spatial_Capabilities>
      <ogc:Spatial_Operators>
        <ogc:Disjoint />
        <ogc:Equals />
        <ogc:DWithin />
        <ogc:Beyond />
        <ogc:Intersect />
        <ogc:Touches />
        <ogc:Crosses />
        <ogc:Within />
        <ogc:Contains />
        <ogc:Overlaps />
        <ogc:BBOX />
      </ogc:Spatial_Operators>
    </ogc:Spatial_Capabilities>
    <ogc:Scalar_Capabilities>
      <ogc:Logical_Operators />
      <ogc:Comparison_Operators>
        <ogc:Simple_Comparisons />
        <ogc:Between />
        <ogc:Like />
        <ogc:NullCheck />
      </ogc:Comparison_Operators>
      <ogc:Arithmetic_Operators>
        <ogc:Simple_Arithmetic />
        <ogc:Functions>
          <ogc:Function_Names>
            <ogc:Function_Name nArgs="1">abs</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">abs_2</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">abs_3</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">abs_4</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">acos</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">AddCoverages</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">Affine</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">Aggregate</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Area</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">area2</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">AreaGrid</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">asin</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">atan</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">atan2</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">BandMerge</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">BandSelect</ogc:Function_Name>
            <ogc:Function_Name nArgs="-6">BarnesSurface</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">between</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">boundary</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">boundaryDimension</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Bounds</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">buffer</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">BufferFeatureCollection</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">bufferWithSegments</ogc:Function_Name>
            <ogc:Function_Name nArgs="7">Categorize</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">ceil</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">centroid</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">classify</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">Clip</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">CollectGeometries</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Average</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Bounds</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">Collection_Count</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Max</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Median</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Min</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Nearest</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Sum</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Collection_Unique</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">Concatenate</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">contains</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">Contour</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">convert</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">convexHull</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">cos</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">Count</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">CropCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">crosses</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">dateFormat</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">dateParse</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">densify</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">difference</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">dimension</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">disjoint</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">disjoint3D</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">distance</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">distance3D</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">double2bool</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">endAngle</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">endPoint</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">env</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">envelope</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">EqualInterval</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">equalsExact</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">equalsExactTolerance</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">equalTo</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">exp</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">exteriorRing</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">Feature</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">floor</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">geometry</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">geometryType</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">geomFromWKT</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">geomLength</ogc:Function_Name>
            <ogc:Function_Name nArgs="-3">GeorectifyCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">GetFullCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">getGeometryN</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">getX</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">getY</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">getz</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">GoGoDuck</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">greaterEqualThan</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">greaterThan</ogc:Function_Name>
            <ogc:Function_Name nArgs="-3">Grid</ogc:Function_Name>
            <ogc:Function_Name nArgs="-5">Heatmap</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">id</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">IEEEremainder</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">if_then_else</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">Import</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">in</ogc:Function_Name>
            <ogc:Function_Name nArgs="11">in10</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">in2</ogc:Function_Name>
            <ogc:Function_Name nArgs="4">in3</ogc:Function_Name>
            <ogc:Function_Name nArgs="5">in4</ogc:Function_Name>
            <ogc:Function_Name nArgs="6">in5</ogc:Function_Name>
            <ogc:Function_Name nArgs="7">in6</ogc:Function_Name>
            <ogc:Function_Name nArgs="8">in7</ogc:Function_Name>
            <ogc:Function_Name nArgs="9">in8</ogc:Function_Name>
            <ogc:Function_Name nArgs="10">in9</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">InclusionFeatureCollection</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">int2bbool</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">int2ddouble</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">interiorPoint</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">interiorRingN</ogc:Function_Name>
            <ogc:Function_Name nArgs="-5">Interpolate</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">intersection</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">IntersectionFeatureCollection</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">intersects</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">intersects3D</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isClosed</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">isCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isEmpty</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isInstanceOf</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">isLike</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isNull</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">isometric</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isRing</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isSimple</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">isValid</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">isWithinDistance</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">isWithinDistance3D</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">Jenks</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">length</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">lessEqualThan</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">lessThan</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">list</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">log</ogc:Function_Name>
            <ogc:Function_Name nArgs="4">LRSGeocode</ogc:Function_Name>
            <ogc:Function_Name nArgs="-4">LRSMeasure</ogc:Function_Name>
            <ogc:Function_Name nArgs="5">LRSSegment</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">max</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">max_2</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">max_3</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">max_4</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">min</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">min_2</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">min_3</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">min_4</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">mincircle</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">minimumdiameter</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">minrectangle</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">modulo</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">MultiplyCoverages</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">Nearest</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">NetcdfOutput</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">not</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">notEqualTo</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">numberFormat</ogc:Function_Name>
            <ogc:Function_Name nArgs="5">numberFormat2</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">numGeometries</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">numInteriorRing</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">numPoints</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">octagonalenvelope</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">offset</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">overlaps</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">PagedUnique</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">parameter</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">parseBoolean</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">parseDouble</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">parseInt</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">parseLong</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">pi</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">PointBuffers</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">pointN</ogc:Function_Name>
            <ogc:Function_Name nArgs="-6">PointStacker</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">PolygonExtraction</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">polygonize</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">pow</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">property</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">PropertyExists</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">Quantile</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">Query</ogc:Function_Name>
            <ogc:Function_Name nArgs="0">random</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">RangeLookup</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">RasterAsPointCollection</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">RasterZonalStatistics</ogc:Function_Name>
            <ogc:Function_Name nArgs="-6">RasterZonalStatistics2</ogc:Function_Name>
            <ogc:Function_Name nArgs="5">Recode</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">RectangularClip</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">relate</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">relatePattern</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">reproject</ogc:Function_Name>
            <ogc:Function_Name nArgs="-1">ReprojectGeometry</ogc:Function_Name>
            <ogc:Function_Name nArgs="-3">rescaleToPixels</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">rint</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">round</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">round_2</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">roundDouble</ogc:Function_Name>
            <ogc:Function_Name nArgs="-5">ScaleCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">setCRS</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">simplify</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">sin</ogc:Function_Name>
            <ogc:Function_Name nArgs="-2">Snap</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">splitPolygon</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">sqrt</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">StandardDeviation</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">startAngle</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">startPoint</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">StoreCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">strCapitalize</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strConcat</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strEndsWith</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strEqualsIgnoreCase</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strIndexOf</ogc:Function_Name>
            <ogc:Function_Name nArgs="4">stringTemplate</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strLastIndexOf</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">strLength</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strMatches</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">strPosition</ogc:Function_Name>
            <ogc:Function_Name nArgs="4">strReplace</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strStartsWith</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">strSubstring</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">strSubstringStart</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">strToLowerCase</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">strToUpperCase</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">strTrim</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">strTrim2</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">StyleCoverage</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">symDifference</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">tan</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">toDegrees</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">toRadians</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">touches</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">toWKT</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">Transform</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">union</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">UnionFeatureCollection</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">Unique</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">UniqueInterval</ogc:Function_Name>
            <ogc:Function_Name nArgs="-4">VectorToRaster</ogc:Function_Name>
            <ogc:Function_Name nArgs="3">VectorZonalStatistics</ogc:Function_Name>
            <ogc:Function_Name nArgs="1">vertices</ogc:Function_Name>
            <ogc:Function_Name nArgs="2">within</ogc:Function_Name>
          </ogc:Function_Names>
        </ogc:Functions>
      </ogc:Arithmetic_Operators>
    </ogc:Scalar_Capabilities>
  </ogc:Filter_Capabilities>
</WFS_Capabilities>''')


TEST_DESCRIBEFEATURETYPE_RESPONSE = httpretty.Response('''<?xml version="1.0" encoding="UTF-8"?><xsd:schema xmlns:gml="http://www.opengis.net/gml" xmlns:imos="imos.mod" xmlns:xsd="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified" targetNamespace="imos.mod">
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
''')

TEST_GETFEATURE_RESPONSE = httpretty.Response('{"type":"FeatureCollection","totalFeatures":780,"features":[{"type":"Feature","id":"soop_trv_duplicate_url.fid-6f08f674_166ec2b1090_-67e1","geometry":null,"properties":{"url":"IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/temperature/IMOS_SOOP-TRV_T_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc"}},{"type":"Feature","id":"soop_trv_duplicate_url.fid-6f08f674_166ec2b1090_-67e0","geometry":null,"properties":{"url":"IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/salinity/IMOS_SOOP-TRV_S_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc"}}],"crs":null}')


class TestSoopTrvHandler(HandlerTestCase):
    @httpretty.activate
    def setUp(self):
        self.handler_class = SoopTrvHandler

        httpretty.register_uri(httpretty.GET, self.config.pipeline_config['global']['wfs_url'],
                               responses=[TEST_GETCAPABILITIES_RESPONSE])
        self.broker = WfsBroker(self.config.pipeline_config['global']['wfs_url'])

        super(TestSoopTrvHandler, self).setUp()


    @httpretty.activate
    def test_good_netcdf(self):
        httpretty.register_uri(httpretty.GET, self.config.pipeline_config['global']['wfs_url'],
                               responses=[TEST_DESCRIBEFEATURETYPE_RESPONSE,
                                          TEST_GETFEATURE_RESPONSE,
                                          TEST_GETCAPABILITIES_RESPONSE,
                                          TEST_GETCAPABILITIES_RESPONSE,
                                          TEST_DESCRIBEFEATURETYPE_RESPONSE,
                                          TEST_GETFEATURE_RESPONSE])

        files_for_layer = self.broker.query_urls_for_layer('soop_trv_duplicate_url')
        self.assertIsInstance(files_for_layer, IndexedSet)

        handler = self.handler_class(GOOD_NC,
                                     include_regexes=['IMOS_SOOP-TRV_B_.*\.nc'],
                                     check_params={'checks': ['cf', 'imos:1.3']}
                                     )
        handler.run()
        latest_requests = httpretty.httpretty.latest_requests

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

    @httpretty.activate
    def test_delete_from_wfs(self):
        httpretty.register_uri(httpretty.GET, self.config.pipeline_config['global']['wfs_url'],
                               responses=[TEST_DESCRIBEFEATURETYPE_RESPONSE, TEST_GETFEATURE_RESPONSE])

        files_for_layer = self.broker.query_urls_for_layer('soop_trv_duplicate_url')

        self.assertIsInstance(files_for_layer, IndexedSet)
        self.assertEqual(files_for_layer[0],
                         'IMOS/SOOP/SOOP-TRV/VMQ9273_Solander/By_Cruise/Cruise_START-20181205T035932Z_END-20181206T045722Z/temperature/IMOS_SOOP-TRV_T_20181205T035932Z_VMQ9273_FV01_END-20181206T045722Z.nc')


if __name__ == '__main__':
    unittest.main()
