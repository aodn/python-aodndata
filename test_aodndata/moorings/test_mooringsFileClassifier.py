import os
import shutil
import unittest
from tempfile import mkdtemp

from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodncore.testlib import BaseTestCase, make_test_file
from aodndata.moorings.classifiers import MooringsFileClassifier


class TestMooringFileClassifier(BaseTestCase):
    """
    Unit tests for MooringsFileClassifier

    Test cases:
    * Temperature loggers
    * CTD_timeseries
    * Biogeochem_timeseries
    * Velocity (ADCP)
    * Wave
    * Biogeochem_profiles
    * non-QC (FV00)
    * burst-averaged
    * gridded
    * NRSMAI long timeseries
    * missing site_code attribute
    * missing featureType attribute

    """

    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_temperature(self):
        filename = 'IMOS_ANMN-NSW_TZ_20150310T130000Z_PH100_FV01_PH100-1503-Aqualogger-520T-16_END-20150606T025000Z_C-20150804T234610Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'PH100', 'featureType': 'timeSeries'},
                       TEMP={},
                       PRES={},
                       DEPTH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NSW/PH100/Temperature')
        self.assertEqual(dest_filename, filename)

    def test_pressure_only(self):
        # Files will only pressure are also classified as "Temperature".
        filename = 'IMOS_ANMN-WA_Z_20120914T032100Z_WATR50_FV01_WATR50-1209-DR-1050-517_END-20130319T053000Z_C-20130325T032512Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'WATR50', 'featureType': 'timeSeries'},
                       PRES={},
                       DEPTH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/WA/WATR50/Temperature')
        self.assertEqual(dest_filename, filename)

    def test_temperature_gridded(self):
        filename = 'IMOS_ANMN-NSW_Temperature_20100702T003500Z_CH070_FV02_CH070-1007-regridded_END-20100907T000500Z_C-20141211T025746Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'CH070', 'featureType': 'timeSeriesProfile'},
                       TEMP={},
                       DEPTH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NSW/CH070/Temperature/gridded')
        self.assertEqual(dest_filename, filename)

    def test_ctd_timeseries(self):
        filename = 'IMOS_ANMN-WA_CSTZ_20141117T080001Z_WATR10_FV01_WATR10-1411-SBE37SM-RS232-52.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'WATR10', 'featureType': 'timeSeries'},
                       TEMP={},
                       PRES={},
                       CNDC={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/WA/WATR10/CTD_timeseries')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-SA_ACESTZ_20141201T030411Z_SAM8SG-1412_FV01_SAM8SG-1412-NXIC-CTD-44.71_END-20150411T020421Z_C-20150730T044018Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'SAM8SG', 'featureType': 'timeSeries'},
                       TEMP={},
                       PRES_REL={},
                       DEPTH={},
                       PSAL={},
                       CNDC={},
                       SSPD={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/SA/SAM8SG/CTD_timeseries')
        self.assertEqual(dest_filename, filename)

    def test_bgc_timeseries(self):
        filename = 'IMOS_ANMN-NRS_KOSTUZ_20150330T080039Z_NRSROT_FV01_NRSROT-1503-WQM-55_END-20150727T063234Z_C-20150731T040136Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSROT', 'featureType': 'timeSeries'},
                       TEMP={},
                       PRES_REL={},
                       DEPTH={},
                       PSAL={},
                       DOX2={},
                       CPHL={},
                       TURB={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSROT/Biogeochem_timeseries')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-QLD_KUZ_20150328T203001Z_GBROTE_FV01_GBROTE-1503-ECO-FLNTUSB-18_END-20151013T030538Z_C-20160225T042413Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'GBROTE', 'featureType': 'timeseries'},
                       DEPTH={},
                       CPHL={},
                       TURB={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/QLD/GBROTE/Biogeochem_timeseries')
        self.assertEqual(dest_filename, filename)

    def test_burst_averaged(self):
        filename = 'IMOS_ANMN-NRS_KOSTUZ_20140808T080100Z_NRSROT_FV02_NRSROT-1408-WQM-55-burst-averaged_END-20141215T234700Z_C-20150319T075400Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSROT', 'featureType': 'timeSeries'},
                       TEMP={},
                       PRES_REL={},
                       DEPTH={},
                       PSAL={},
                       DOX2={},
                       CPHL={},
                       TURB={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSROT/Biogeochem_timeseries/burst-averaged')
        self.assertEqual(dest_filename, filename)

    def test_velocity(self):
        filename = 'IMOS_ANMN-NRS_AETVZ_20150703T053000Z_NRSROT-ADCP_FV01_NRSROT-ADCP-1507-Workhorse-ADCP-43_END-20151023T034500Z_C-20151117T074309Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSROT'},
                       TEMP={},
                       PRES_REL={},
                       DEPTH={},
                       UCUR={},
                       VCUR={},
                       WCUR={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSROT/Velocity')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-NRS_AETVZ_20150703T053000Z_NRSROT-ADCP_FV00_NRSROT-ADCP-1507-Workhorse-ADCP-43_END-20151023T034500Z_C-20151117T074309Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSROT'},
                       UCUR_MAG={},
                       VCUR_MAG={},
                       CSPD={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSROT/Velocity/non-QC')
        self.assertEqual(dest_filename, filename)

    def test_wave(self):
        filename = 'IMOS_ANMN-NRS_WZ_20140914T075900Z_NRSDAR_FV01_NRSDAR-1409-SUB-Workhorse-ADCP-24.3_END-20150205T225900Z_C-20150326T055936Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSDAR', 'featureType': 'doesntmatter'},
                       DEPTH={},
                       VAVH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSDAR/Wave')
        self.assertEqual(dest_filename, filename)

    def test_bgc_profiles(self):
        filename = 'IMOS_ANMN-NRS_CDEKOSTUZ_20121113T001841Z_NRSMAI_FV00_Profile-SBE-19plus_C-20151030T034432Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSMAI', 'featureType': 'profile'},
                       TEMP={},
                       PRES={},
                       CNDC={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSMAI/Biogeochem_profiles/non-QC')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-WA_CDEKOSTUZ_20121113T013800Z_WACA20_FV01_3052.0-1-SBE19plus-70_C-20140211T090215Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'WACA20', 'featureType': 'profile'},
                       TEMP={},
                       PRES_REL={},
                       PSAL={},
                       DOX2={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/WA/WACA20/Biogeochem_profiles')
        self.assertEqual(dest_filename, filename)

    def test_long_timeseries(self):
        filename = 'IMOS_ANMN-NRS_STZ_19441015T000000Z_NRSMAI_FV02_NRSMAI-long-timeseries_END-20140703T000000Z_C-20160525T064856Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSMAI', 'featureType': 'timeSeriesProfile'},
                       TEMP={},
                       PSAL={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSMAI/aggregated_products')
        self.assertEqual(dest_filename, filename)

    def test_unknown_product(self):
        filename = 'IMOS_ANMN-NRS_STZ_20170101T000000Z_NRSMAI_FV02.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSMAI', 'featureType': 'timeSeriesProfile'},
                       TEMP={},
                       PSAL={}
                       )
        with self.assertRaisesRegexp(InvalidFileNameError, "Can't determine product type from file name"):
            MooringsFileClassifier.dest_path(testfile)

    def test_unknown_profiles(self):
        filename = 'IMOS_ANMN-NRS_CDEKOSTUZ_20121113T001841Z_NRSMAI_FV00_mystery-profile.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSMAI', 'featureType': 'profile'},
                       TIME={},
                       DEPTH={}
                       )
        with self.assertRaisesRegexp(InvalidFileContentError, "Could not determine data category"):
            MooringsFileClassifier.dest_path(testfile)

    def test_nonqc(self):
        filename = 'IMOS_ANMN-NSW_TZ_20150310T130000Z_PH100_FV00_PH100-1503-Aqualogger-520T-16_END-20150606T025000Z_C-20150804T234610Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile,
                       {'site_code': 'PH100', 'featureType': 'timeSeries', 'file_version': 'Level 0 - Raw data'},
                       TEMP={},
                       PRES={},
                       DEPTH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NSW/PH100/Temperature/non-QC')
        self.assertEqual(dest_filename, filename)

    def test_missing_site_code(self):
        testfile = os.path.join(self.tempdir, 'IMOS_ANMN-NRS_CDEKOSTUZ_20121113T001841Z_BADBAD_FV01_Profile.nc')
        make_test_file(testfile)
        with self.assertRaisesRegexp(InvalidFileContentError, "has no attribute 'site_code'"):
            MooringsFileClassifier.dest_path(testfile)

    def test_missing_featuretype(self):
        testfile = os.path.join(self.tempdir,
                                'IMOS_ANMN-NRS_CDEKOSTUZ_20121113T001841Z_NRSMAI_FV01_Profile-SBE-19plus_C-20151030T034432Z.nc')
        make_test_file(testfile, {'site_code': 'NRSMAI'})
        with self.assertRaisesRegexp(InvalidFileContentError, "has no attribute 'featureType'"):
            MooringsFileClassifier.dest_path(testfile)

    def test_logsheet(self):
        filename = 'IMOS_ANMN-NRS_100702_NRSPHB_FV00_LOGSHT.pdf'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSPHB/Field_logsheets')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-NRS_20150804T043000Z_NRSDAR_FV01_LOGSHT.pdf'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSDAR/Field_logsheets')
        self.assertEqual(dest_filename, filename)

    def test_cnv(self):
        filename = 'IMOS_ANMN-NRS_CTP_090527_NRSNSI_FV00_CTDPRO.cnv'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSNSI/Biogeochem_profiles/non-QC/cnv')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-NRS_CTP_120729T163000Z_NRSDAR_FV00_CTDPRO_01.cnv'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSDAR/Biogeochem_profiles/non-QC/cnv')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-NRS_CDEKOSTUZ_140730_NRSROT_FV00_CTDPRO.cnv'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSROT/Biogeochem_profiles/non-QC/cnv')
        self.assertEqual(dest_filename, filename)

    def test_plots(self):
        filename = 'IMOS_ANMN-WA_WATR20_FV01_WATR20-1502_LINE_TEMP_C-20150820T052407Z.png'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/WA/WATR20/plots')
        self.assertEqual(dest_filename, filename)

        filename = 'IMOS_ANMN-NRS_NRSMAI-ADCP_FV01_NRSMAI-ADCP-09-2015-04_SCATTER_UCUR_C-20160104T032431Z.png'
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(filename))
        self.assertEqual(dest_dir, 'IMOS/ANMN/NRS/NRSMAI/plots')
        self.assertEqual(dest_filename, filename)

    def test_acidification_mooring_delayed(self):
        filename = 'IMOS_ANMN-AM_GST_20170912T060000Z_NRSMAI_FV01_NRSMAI-CO2-1709-delayed_END_20180419T230000Z_C-20180716T102404Z.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile,
                       {'site_code': 'NRSMAI'},
                       TEMP={},
                       PSAL={},
                       Press_ATM={},
                       xCO2EQ_PPM={},
                       xCO2ATM_PPM={},
                       fCO2SW_UATM={},
                       DOX1={},
                       TPH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/AM/NRSMAI/CO2/delayed')
        self.assertEqual(dest_filename, filename)

    def test_acidification_mooring_realtime(self):
        filename = 'IMOS_ANMN-AM_GST_20180926T000000Z_NRSMAI_FV01_NRSMAI-CO2-1809-realtime.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile,
                       {'site_code': 'NRSMAI'},
                       TEMP={},
                       PSAL={},
                       Press_ATM={},
                       xCO2EQ_PPM={},
                       xCO2ATM_PPM={},
                       fCO2SW_UATM={},
                       DOX1={},
                       TPH={}
                       )
        dest_dir, dest_filename = os.path.split(MooringsFileClassifier.dest_path(testfile))
        self.assertEqual(dest_dir, 'IMOS/ANMN/AM/NRSMAI/CO2/real-time')
        self.assertEqual(dest_filename, filename)

    def test_acidification_mooring_invalid(self):
        filename = 'IMOS_ANMN-AM_GST_20180926T000000Z_NRSMAI_FV01_NRSMAI-CO2-1809.nc'
        testfile = os.path.join(self.tempdir, filename)
        make_test_file(testfile, {'site_code': 'NRSMAI'}, xCO2EQ_PPM={})
        self.assertRaises(InvalidFileNameError, MooringsFileClassifier.dest_path, testfile)


if __name__ == '__main__':
    unittest.main()
