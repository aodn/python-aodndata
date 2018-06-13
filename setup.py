import os
from itertools import chain

from pip.req import parse_requirements
from pkg_resources import EntryPoint
from setuptools import setup, find_packages

from aodndata.version import __version__

ENTRY_POINTS = {
    'pipeline.handlers': [
        'AatamsNrtHandler = aodndata.aatams.aatams_nrt:AatamsNrtHandler',
        'AbosHandler = aodndata.moorings.handlers:AbosHandler',
        'AnmnNrsAimsHandler = aodndata.aims.anmn_nrs:AnmnNrsAimsHandler',
        'AuvHandler = aodndata.auv.handler:AuvHandler',
        'ArgoHandler = aodndata.argo.handler:ArgoHandler',
        'AsyncUploadHandler = aodndata.common.asyncupload:AsyncUploadHandler',
        'FaimmsHandler = aodndata.aims.faimms:FaimmsHandler',
        'GenericHandler = aodndata.common.generic:GenericHandler',
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
        'SoopCo2Handler = aodndata.soop.soop_co2:SoopCo2Handler'

    ],
    'pipeline.path_functions': [
        'dest_path_aatams_sattag_qc_ctd = aodndata.aatams:dest_path_aatams_sattag_qc_ctd',
        'dest_path_anmn_nrs_realtime = aodndata.moorings.classifiers:dest_path_anmn_nrs_realtime',
        'dest_path_cars = aodndata.csiro.cars:dest_path_cars',
        'dest_path_sstaars = aodndata.csiro.sstaars:dest_path_sstaars',
        'dest_path_deakin_bathymetry = aodndata.deakin.deakin_bathymetry:dest_path_deakin_bathymetry',
        'dest_path_oa = aodndata.csiro.ocean_acidification:dest_path_oa',
        'dest_path_soop_xbt_nrt = aodndata.soop.soop_xbt_nrt:dest_path_soop_xbt_nrt'
    ],
    'pipeline.module_versions': [
        'aodndata = aodndata.version:__version__'
    ]
}

# validate entry points
for item in chain(ENTRY_POINTS['pipeline.handlers'], ENTRY_POINTS['pipeline.path_functions']):
    if item.count('=') != 1:
        raise ValueError("invalid entry point '{item}'. Missing comma?".format(item=item))
    try:
        EntryPoint.parse(item).resolve()
    except Exception as e:
        raise ValueError("invalid entry point '{item}'. {c}: {e}".format(item=item, c=e.__class__.__name__, e=e))

PACKAGE_EXCLUDES = ['test_aodndata.*', 'test_aodndata']
PACKAGE_NAME = 'aodndata'

package_root = os.path.dirname(os.path.realpath(__file__))
requirements_txt = os.path.join(package_root, 'requirements.txt')

requires = [str(r.req) for r in parse_requirements(requirements_txt, session=False)]

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
    install_requires=requires,
    test_suite='test_aodndata',
    entry_points=ENTRY_POINTS
)
