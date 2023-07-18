import datetime
import numpy as np
import os
import unittest
from unittest.mock import patch

from netCDF4 import Dataset

from aodncore.pipeline import PipelineFilePublishType, FileType, PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidFileContentError
from aodncore.testlib import HandlerTestCase
from aodndata.soop.soop_xbt_nrt import SoopXbtNrtHandler, xbt_line_get_info, parse_bufr_file, \
    fzf_vessel_get_info
from aodndata.soop.ship_callsign import ship_callsign_list

TEST_ROOT = os.path.join(os.path.dirname(__file__))

TEST_PLATFORM_VOCAB_URL = '%s%s' % ('file://',
                                    os.path.join(TEST_ROOT, 'aodn_aodn-platform-vocabulary.rdf'))
TEST_XBT_LINE_VOCAB_URL = '%s%s' % ('file://',
                                    os.path.join(TEST_ROOT, 'aodn_aodn-xbt-line-vocabulary.rdf'))

GOOD_BUFR_CSV = os.path.join(TEST_ROOT,
                       'IOSS01_AMMC_20201109215900_XEKXW9W.csv')
GOOD_BUFR_CSV_PX30 = os.path.join(TEST_ROOT,
                                  'IOSS01_AMMC_20201214180200_5VULUEH.csv')
GOOD_BUFR_BIN_CSIRO = os.path.join(TEST_ROOT,
                             'IOSS01_AMMC_20221231231505_XEKXW9W.bin')
GOOD_BUFR_BIN_BOM = os.path.join(TEST_ROOT,
                             'IOSS01_AMMC_202307162000.bin')
BUFR_CSV_NO_LINE = os.path.join(TEST_ROOT,
                                  'IOSS01_AMMC_20200908051000_VLMJ.csv')

BUFR_ALTERNATIVE_ASTROLABE_NAME = os.path.join(TEST_ROOT,
                                               'IOSS01_AMMC_20211204160500_XEKXW9W.csv')


def mock_platform_altlabels_per_preflabel(category_name='Vessel'):
    return {'VLHJ': 'Southern-Surveyor',
            '9V2768': 'RTM-Wakmatha',
            'FHZI': 'Astrolabe',
            'FASB': 'Astrolabe',
            '3FLZ': 'Tropical-Islander',
            'VROJ8': 'Highland-Chief',
            'VROB': 'Highland-Chief',
            'D5LR9': 'Seatrade Red',
            'VLMJ': 'Investigator',
            'VRDE7': 'OOCL Houston',
            }


class TestSoopXbtNrtHandler(HandlerTestCase):
    def setUp(self):
        ship_callsign_list.cache_clear()  # ship_callsign is called in previous test_ship_callsign unittest which is
        # not including all mocked values in mock_platform_altlabels_per_preflabel function above. ship_callsign_list()
        # is using the lru_cache decorator. We're forcing in this unittest the clearing of all cached values.

        self.handler_class = SoopXbtNrtHandler
        super(TestSoopXbtNrtHandler, self).setUp()
        self.url = TEST_XBT_LINE_VOCAB_URL
        self.good_profile = ({
            'profile_metadata':  ({''
                                   'XBT_line': "IX8",
                                   'ship_name': "L'Astrolabe"
                                   })
        })
        self.bad_profile = ({
            'profile_metadata':  ({''
                                   'XBT_line': "XXXX",
                                   'ship_name': "L\'Astrolab"
                                   })
        })
        self.px30_31 = ({
            'profile_metadata':  ({''
                                   'XBT_line': "PX30",
                                   'ship_name': "Seatrade Red"
                                   })
        })

    def test_bufr_parser(self):
        """
        test the bufr_parser function outputs
        :return:
        """
        profiles = parse_bufr_file(GOOD_BUFR_CSV)
        profile = profiles[0]  # check first profile data

        self.assertEqual(-53.58368, profile['profile_geotime']['latitude'])
        self.assertEqual(146.23137, profile['profile_geotime']['longitude'])
        self.assertEqual(datetime.datetime(2020, 11, 9, 21, 59),
                         profile['profile_geotime']['date_utc'])

        self.assertAlmostEqual(36.26, profile['profile_data']['temp'].max())  # obviously not a quality controlled value
        self.assertAlmostEqual(1.78, profile['profile_data']['temp'].min())
        self.assertEqual(1110.39, profile['profile_data']['depth'].max())
        self.assertEqual(0, profile['profile_data']['depth'].min())
        self.assertEqual(1577, len(profile['profile_data']['depth']))
        self.assertEqual(1577, len(profile['profile_data']['temp']))
        self.assertEqual("1218367", profile['profile_metadata']['XBT_instrument_serialnumber'])
        self.assertEqual("9797539", profile['profile_metadata']['imo_number'])

        self.assertEqual("WMO Code table 4770 code \"72, TURO/CSIRO Quoll XBT acquisition system\"",
                         profile['profile_metadata']['XBT_recorder_type'])

        self.assertEqual("WMO Code Table 1770 \"probe=Sippican Deep Blue,code=052,a=6.691,b=-2.25\"",
                         profile['profile_metadata']['XBT_probetype_fallrate_equation'])

    def test_xbt_line_get_info(self):
        """
        test the xbt_line_get_info function which reads the XBT ANDS vocabulary
        :return:
        """
        # add RDF test file from pipeline_config['global']['xbt_line_vocab_url']
        good_profile = xbt_line_get_info(self.good_profile, self.url)

        self.assertEqual("IX08", good_profile['profile_metadata']['XBT_line'])
        self.assertEqual("Mauritius - Bombay", good_profile['profile_metadata']['XBT_line_description'])

        # the xbt_line_get_info forces in some case the vocabulary inconsistencies
        px30_31_line = xbt_line_get_info(self.px30_31, self.url)
        self.assertEqual("PX30-31", px30_31_line['profile_metadata']['XBT_line'])
        self.assertEqual("Brisbane - Noumea - Suva", px30_31_line['profile_metadata']['XBT_line_description'])

        # check with a bad value of XBT line
        with self.assertRaises(InvalidFileContentError):
            xbt_line_get_info(self.bad_profile, self.url)

    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_fzf_vessel_info(self, mock_ship):
        """
        Check fuzzy find match for a vessel name and callsign between the value found in the BUFR file and the XBT line
        ANDS vocabulary
        :return:
        """
        # check fuzzy search match SUCCESS with a good enough vessel name
        good_profile = fzf_vessel_get_info(self.good_profile)

        self.assertEqual("Astrolabe", good_profile['profile_metadata']['ship_name'])
        self.assertEqual("FASB", good_profile['profile_metadata']['Callsign'])

        # check fuzzy search match FAIL with a NOT good enough vessel name
        with self.assertRaises(InvalidFileContentError):
            fzf_vessel_get_info(self.bad_profile)

    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_handler(self, mock_ship):
        handler = self.run_handler(GOOD_BUFR_CSV,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        f_csv = handler.file_collection.filter_by_attribute_id('file_type', FileType.CSV)[0]

        self.assertEqual(f_csv.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME_BUFR/2020/',
                                      os.path.basename(GOOD_BUFR_CSV)),
                         f_csv.archive_path)

        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME/FASB_Astrolabe/2020/',
                                      'IMOS_SOOP-XBT_T_20201109T215900Z_IX28_FV00_ID_9797539.nc'),
                         f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        nc_path = os.path.join(self.config.pipeline_config['global']['upload_uri'], f_nc.dest_path).replace("file://",
                                                                                                            "")
        with Dataset(nc_path, mode='r') as nc_obj:
            self.assertEqual("Hobart - Dumont d'Urville", nc_obj.XBT_line_description)
            self.assertEqual("Upper Ocean Thermal Data collected on the high density line IX28 "
                             "(Dumont d Urville-Hobart) using XBT (expendable bathythermographs)", nc_obj.title)

            self.assertEqual(6.691, nc_obj['DEPTH'].fallrate_equation_coefficient_a)
            self.assertEqual(-2.25, nc_obj['DEPTH'].fallrate_equation_coefficient_b)
            self.assertEqual(1110.39, nc_obj.geospatial_vertical_max)

        # test the handler by pushing this newly created NetCDF file back into the handler
        handler = self.run_handler(nc_path,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)

    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_handler_bufr_bin_csiro(self, mock_ship):
        """
        Run Handler on a BUFR Bin format which should be automatically converted into a BUFR text format, then into a NetCDF
        :param mock_ship:
        :return:
        """
        handler = self.run_handler(GOOD_BUFR_BIN_CSIRO,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        f_bin = handler.file_collection.filter_by_attribute_regex('extension', '.bin')[0]

        self.assertEqual(f_bin.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME_BUFR/2022/',
                                      os.path.basename(GOOD_BUFR_BIN_CSIRO)),
                         f_bin.archive_path)

        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME/FASB_Astrolabe/2022/',
                                      'IMOS_SOOP-XBT_T_20221231T225500Z_IX28_FV00_ID_9797539.nc'),
                         f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        nc_path = os.path.join(self.config.pipeline_config['global']['upload_uri'], f_nc.dest_path).replace("file://",
                                                                                                            "")
        with Dataset(nc_path, mode='r') as nc_obj:
            self.assertEqual("Hobart - Dumont d'Urville", nc_obj.XBT_line_description)
            self.assertEqual("Upper Ocean Thermal Data collected on the high density line IX28 "
                             "(Dumont d Urville-Hobart) using XBT (expendable bathythermographs)", nc_obj.title)

            self.assertEqual(6.691, nc_obj['DEPTH'].fallrate_equation_coefficient_a)
            self.assertEqual(-2.25, nc_obj['DEPTH'].fallrate_equation_coefficient_b)
            self.assertEqual(10282.47, nc_obj.geospatial_vertical_max)

    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_handler_bufr_bin_bom(self, mock_ship):
        """
        Run Handler on a BUFR Bin format which should be automatically converted into a BUFR text format, then into a NetCDF
        :param mock_ship:
        :return:
        """
        handler = self.run_handler(GOOD_BUFR_BIN_BOM,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})
        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        f_bin = handler.file_collection.filter_by_attribute_regex('extension', '.bin')[0]

        self.assertEqual(f_bin.publish_type, PipelineFilePublishType.ARCHIVE_ONLY)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME_BUFR/2023/',
                                      os.path.basename(GOOD_BUFR_BIN_BOM)),
                         f_bin.archive_path)

        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME/VRDE7_OOCL-Houston/2023/',
                                      'IMOS_SOOP-XBT_T_20230716T184700Z_PX2_FV00_ID_8008872.nc'),
                         f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

        nc_path = os.path.join(self.config.pipeline_config['global']['upload_uri'], f_nc.dest_path).replace("file://",
                                                                                                            "")
        with Dataset(nc_path, mode='r') as nc_obj:
            self.assertEqual("Flores Sea - Torres Strait", nc_obj.XBT_line_description)
            self.assertEqual("Upper Ocean Thermal Data collected on the line PX2 "
                             "(Across the Banda Sea) using XBT (expendable bathythermographs)", nc_obj.title)

            self.assertEqual(6.691, nc_obj['DEPTH'].fallrate_equation_coefficient_a)
            self.assertEqual(-2.25, nc_obj['DEPTH'].fallrate_equation_coefficient_b)
            self.assertEqual(477.0, nc_obj.geospatial_vertical_max)
            self.assertEqual(16.0, np.round(np.mean(nc_obj['TEMP'][:])))


    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_handler_px30(self, mock_ship):
        handler = self.run_handler(GOOD_BUFR_CSV_PX30,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME/D5LR9_Seatrade-Red/2020/',
                                      'IMOS_SOOP-XBT_T_20201214T180200Z_PX30-31_FV00_ID_9690107.nc'),
                         f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)


    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_handler_noline(self, mock_ship):
        handler = self.run_handler(BUFR_CSV_NO_LINE,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME/VLMJ_Investigator/2020/',
                                      'IMOS_SOOP-XBT_T_20200908T051000Z_NOLINE_FV00.nc'),
                         f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)

    @patch("aodndata.soop.ship_callsign.platform_altlabels_per_preflabel",
           side_effect=mock_platform_altlabels_per_preflabel)
    def test_alternative_astrolabe_name(self, mock_ship):
        handler = self.run_handler(BUFR_ALTERNATIVE_ASTROLABE_NAME,
                                   check_params={'checks': ['cf:1.6']},
                                   custom_params={'xbt_line_vocab_url': TEST_XBT_LINE_VOCAB_URL})

        f_nc = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        self.assertEqual(f_nc.publish_type, PipelineFilePublishType.HARVEST_UPLOAD)
        self.assertEqual(os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME/FASB_Astrolabe/2021/',
                                      'IMOS_SOOP-XBT_T_20211204T160500Z_IX28_FV00_ID_9797539.nc'),
                         f_nc.dest_path)
        self.assertEqual(f_nc.check_type, PipelineFileCheckType.NC_COMPLIANCE_CHECK)


if __name__ == '__main__':
    unittest.main()
