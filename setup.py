from itertools import chain
from setuptools import setup, find_packages

ENTRY_POINTS = {
    'pipeline.handlers': [
        'AatamsSattagQcDmHandler = aodndata.aatams.aatams_sattag:AatamsSattagQcDmHandler',
        'AatamsSattagQcNrtHandler = aodndata.aatams.aatams_sattag:AatamsSattagQcNrtHandler',
        'AbosHandler = aodndata.moorings.handlers:AbosHandler',
        'AnfogHandler = aodndata.anfog.handlers:AnfogHandler',
        'AcornHandler = aodndata.acorn.handler:AcornHandler',
        'AnmnNrsAimsHandler = aodndata.aims.anmn_nrs:AnmnNrsAimsHandler',
        'AuvHandler = aodndata.auv.handler:AuvHandler',
        'ArgoHandler = aodndata.argo.handler:ArgoHandler',
        'AsyncUploadHandler = aodndata.common.asyncupload:AsyncUploadHandler',
        'DwmHandler = aodndata.moorings.handlers:DwmHandler',
        'FaimmsHandler = aodndata.aims.faimms:FaimmsHandler',
        'GenericHandler = aodndata.common.generic:GenericHandler',
        'GslaHandler = aodndata.gsla.handler:GslaHandler',
        'MooringsHandler = aodndata.moorings.handlers:MooringsHandler',
        'MooringsProductsHandler = aodndata.moorings.products_handler:MooringsProductsHandler',
        'NswOehHandler = aodndata.nsw_oeh.handler:NswOehHandler',
        'SoopAsfSstHandler = aodndata.soop.soop_asf_sst:SoopAsfSstHandler',
        'SoopBaHandler = aodndata.soop.soop_ba:SoopBaHandler',
        'SoopTrvHandler = aodndata.soop.soop_trv:SoopTrvHandler',
        'SoopXbtDmHandler = aodndata.soop.soop_xbt_dm:SoopXbtDmHandler',
        'SoopXbtNrtHandler = aodndata.soop.soop_xbt_dm:SoopXbtNrtHandler',
        'SrsAltHandler = aodndata.srs.srs_altimetry:SrsAltHandler',
        'SrsGhrsstHandler = aodndata.srs.srs_ghrsst:SrsGhrsstHandler',
        'SrsOcBodBawHandler = aodndata.srs.srs_oc_bodbaw:SrsOcBodBawHandler',
        'SrsOcGriddedHandler = aodndata.srs.srs_oc_gridded:SrsOcGriddedHandler',
        'SrsOcLjcoHandler = aodndata.srs.srs_oc_ljco:SrsOcLjcoHandler',
        'SrsOcSoopRadHandler = aodndata.srs.srs_oc_soop_rad:SrsOcSoopRadHandler',
        'SstaarsHandler = aodndata.csiro.sstaars:SstaarsHandler',
        'SoopCo2Handler = aodndata.soop.soop_co2:SoopCo2Handler',
        'SoopTmvNrtHandler = aodndata.soop.soop_tmv_nrt:SoopTmvNrtHandler'
    ],
    'pipeline.path_functions': [
        'dest_path_aatams_sattag_qc_ctd = aodndata.aatams:dest_path_aatams_sattag_qc_ctd',
        'dest_path_anmn_nrs_realtime = aodndata.moorings.classifiers:dest_path_anmn_nrs_realtime',
        'dest_path_aodn_wave_dm = aodndata.aodn_wave_dm.aodn_wave_dm:dest_path_aodn_wave_dm',
        'dest_path_cars = aodndata.csiro.cars:dest_path_cars',
        'dest_path_deakin_bathymetry = aodndata.deakin.deakin_bathymetry:dest_path_deakin_bathymetry',
        'dest_path_soop_rad_aodn = aodndata.curtin.soop_rad_aodn:dest_path_soop_rad_aodn',
        'dest_path_oa = aodndata.csiro.ocean_acidification:dest_path_oa',
        'dest_path_srs_oc_ljco_aeronet = aodndata.srs.srs_oc_ljco_aeronet:dest_path_srs_oc_ljco_aeronet',
        'dest_path_srs_surface_waves = aodndata.srs.srs_surface_waves:dest_path_srs_surface_waves',
        'dest_path_srs_surface_waves_sar = aodndata.srs.srs_surface_waves:dest_path_srs_surface_waves_sar'
    ],
    'pipeline.module_versions': [
        'aodndata = aodndata.version:__version__',
        'cc-plugin-imos = cc_plugin_imos:__version__',
        'aodntools = aodntools:__version__'
    ]
}

INSTALL_REQUIRES = [
    'aodntools>=1.3.1',  # installed before aodncore due to more specific jsonschema dependency
    'aodncore>=1.0.0',
    'cc-plugin-imos>=1.3.0',
    'fiona>=1.8.8',
    'fuzzywuzzy>=0.18.0',  # most used python fuzzy search finder
    'matplotlib>=3.0.3',
    'pillow>=6.2.1,<7.0.0',  # provide additional image formats for matplotlib
    'schema>=0.7.0'
]

TESTS_REQUIRE = [
    'httpretty',
    'pytest',
    'testfixtures'
]

EXTRAS_REQUIRE = {
    'testing': TESTS_REQUIRE
}

# validate entry points
for item in chain(ENTRY_POINTS['pipeline.handlers'], ENTRY_POINTS['pipeline.path_functions']):
    if item.count('=') != 1:
        raise ValueError("invalid entry point '{item}'. Missing comma?".format(item=item))

PACKAGE_EXCLUDES = ['test_aodndata.*', 'test_aodndata']
PACKAGE_NAME = 'aodndata'

setup(
    name=PACKAGE_NAME,
    version='1.3.23',
    packages=find_packages(exclude=PACKAGE_EXCLUDES),
    url='https://github.com/aodn',
    license='GPLv3',
    author='AODN',
    author_email='developers@emii.org.au',
    description='AODN pipeline library',
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    tests_require=TESTS_REQUIRE,
    test_suite='test_aodndata',
    entry_points=ENTRY_POINTS,
    include_package_data=True,
    package_data={'aodndata': ['templates/*.json',
                               'configurations/*.ini']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
