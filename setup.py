import os

from pip.req import parse_requirements
from setuptools import setup, find_packages

from aodndata.version import __version__

ENTRY_POINTS = {
    'pipeline.handlers': [
        'AatamsNrtHandler = aodndata.aatams.aatams_nrt:AatamsNrtHandler',
        'AnmnNrsAimsHandler = aodndata.aims.anmn_nrs:AnmnNrsAimsHandler',
        'AuvHandler = aodndata.auv.handler:AuvHandler',
        'ArgoHandler = aodndata.argo.handler:ArgoHandler',
        'AsyncUploadHandler = aodndata.common.asyncupload:AsyncUploadHandler',
        'FaimmsHandler = aodndata.aims.faimms:FaimmsHandler',
        'GenericHandler = aodndata.common.generic:GenericHandler',
        'MooringsHandler = aodndata.moorings.handlers:MooringsHandler',
        'SoopAsfSstHandler = aodndata.soop.soop_asf_sst:SoopAsfSstHandler',
        'SoopTrvHandler = aodndata.soop.soop_trv:SoopTrvHandler',
        'SoopXbtDmHandler = aodndata.soop.soop_xbt_dm:SoopXbtDmHandler',
        'SoopXbtNrtHandler = aodndata.soop.soop_xbt_nrt:SoopXbtNrtHandler',
        'SrsAltHandler = aodndata.srs.srs_altimetry:SrsAltHandler',
        'SrsGhrsstHanlder = aodndata.srs.srs_ghrsst:SrsGhrsstHandler',
        'SrsOcBodBawHandler = aodndata.srs.srs_oc_bodbaw:SrsOcBodBawHandler',
        'SrsOcLjcoHandler = aodndata.srs.srs_oc_ljco:SrsOcLjcoHandler',
        'SoopCo2Handler = aodndata.soop.soop_co2:SoopCo2Handler'

    ],
    'pipeline.path_functions': [
        'dest_path_aatams_sattag_qc_ctd = aodndata.aatams:dest_path_aatams_sattag_qc_ctd',
        'dest_path_anmn_nrs_realtime = aodndata.moorings.classifiers:dest_path_anmn_nrs_realtime'
    ]
}

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
