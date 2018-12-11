from __future__ import absolute_import
from __future__ import unicode_literals
from itertools import chain
from pkg_resources import EntryPoint
from setuptools import setup, find_packages

from aodndata.version import __version__

ENTRY_POINTS = {
    'pipeline.handlers': [
        'AatamsNrtHandler = aodndata.aatams.aatams_nrt:AatamsNrtHandler',
        'AbosHandler = aodndata.moorings.handlers:AbosHandler',
        'AnfogHandler = aodndata.anfog.handlers:AnfogHandler',
        'AcornHandler = aodndata.acorn.handler:AcornHandler',
        'AnmnNrsAimsHandler = aodndata.aims.anmn_nrs:AnmnNrsAimsHandler',
        'AuvHandler = aodndata.auv.handler:AuvHandler',
        'ArgoHandler = aodndata.argo.handler:ArgoHandler',
        'AsyncUploadHandler = aodndata.common.asyncupload:AsyncUploadHandler',
        'FaimmsHandler = aodndata.aims.faimms:FaimmsHandler',
        'GenericHandler = aodndata.common.generic:GenericHandler',
        'GslaHandler = aodndata.gsla.handler:GslaHandler',
        'MooringsHandler = aodndata.moorings.handlers:MooringsHandler',
        'SoopAsfSstHandler = aodndata.soop.soop_asf_sst:SoopAsfSstHandler',
        'SoopBaHandler = aodndata.soop.soop_ba:SoopBaHandler',
        'SoopTrvHandler = aodndata.soop.soop_trv:SoopTrvHandler',
        'SoopXbtDmHandler = aodndata.soop.soop_xbt_dm:SoopXbtDmHandler',
        'SrsAltHandler = aodndata.srs.srs_altimetry:SrsAltHandler',
        'SrsGhrsstHandler = aodndata.srs.srs_ghrsst:SrsGhrsstHandler',
        'SrsOcBodBawHandler = aodndata.srs.srs_oc_bodbaw:SrsOcBodBawHandler',
        'SrsOcGriddedHandler = aodndata.srs.srs_oc_gridded:SrsOcGriddedHandler',
        'SrsOcLjcoHandler = aodndata.srs.srs_oc_ljco:SrsOcLjcoHandler',
        'SrsOcSoopRadHandler = aodndata.srs.srs_oc_soop_rad:SrsOcSoopRadHandler',
        'SstaarsHandler = aodndata.csiro.sstaars:SstaarsHandler',
        'SoopCo2Handler = aodndata.soop.soop_co2:SoopCo2Handler'
    ],
    'pipeline.path_functions': [
        'dest_path_aatams_sattag_qc_ctd = aodndata.aatams:dest_path_aatams_sattag_qc_ctd',
        'dest_path_anmn_nrs_realtime = aodndata.moorings.classifiers:dest_path_anmn_nrs_realtime',
        'dest_path_aodn_wave_dm = aodndata.aodn_wave_dm.aodn_wave_dm:dest_path_aodn_wave_dm',
        'dest_path_cars = aodndata.csiro.cars:dest_path_cars',
        'dest_path_deakin_bathymetry = aodndata.deakin.deakin_bathymetry:dest_path_deakin_bathymetry',
        'dest_path_oa = aodndata.csiro.ocean_acidification:dest_path_oa',
        'dest_path_soop_xbt_nrt = aodndata.soop.soop_xbt_nrt:dest_path_soop_xbt_nrt',
        'dest_path_srs_surface_waves = aodndata.srs.srs_surface_waves:dest_path_srs_surface_waves'
    ],
    'pipeline.module_versions': [
        'aodndata = aodndata.version:__version__',
        'cc-plugin-imos = cc_plugin_imos:__version__'
    ]
}

INSTALL_REQUIRES = [
    'aodncore>=0.12.0',
    'cc-plugin-imos>=1.3.0',
    'matplotlib==1.5.1',
    'pandas==0.22.0'
]

EXTRAS_REQUIRE = {
    ':python_version < "3.2"': ['functools32 == 3.2.3-2']
}


# validate entry points
for item in chain(ENTRY_POINTS['pipeline.handlers'], ENTRY_POINTS['pipeline.path_functions']):
    if item.count('=') != 1:
        raise ValueError("invalid entry point '{item}'. Missing comma?".format(item=item))

PACKAGE_EXCLUDES = ['test_aodndata.*', 'test_aodndata']
PACKAGE_NAME = 'aodndata'

setup(
    name=PACKAGE_NAME,
    version=__version__,
    packages=find_packages(exclude=PACKAGE_EXCLUDES),
    url='https://github.com/aodn',
    license='GPLv3',
    author='AODN',
    author_email='developers@emii.org.au',
    description='AODN pipeline library',
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    test_suite='test_aodndata',
    entry_points=ENTRY_POINTS
)
