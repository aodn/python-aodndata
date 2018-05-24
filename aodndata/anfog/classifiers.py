import os
import re

from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileNameError


class AnfogFileClassifier(FileClassifier):
    MISSION_LISTING = 'HarvestmissionList.csv'
    ANFOG_RT_REGEX = \
        '^IMOS_ANFOG.*_[0-9]{8}T[0-9]{6}Z_.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    ANFOG_DM_REGEX = \
        '^IMOS_ANFOG.*_[0-9]{8}T[0-9]{6}Z.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_REGEX = '^DSTO_.*_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_BASE = 'Department_of_Defence/DSTG'
    NRL_REGEX = '^NRL_.*_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    NRL_BASE = 'US_Naval_Research_Laboratory'
    DM_REGEX = '.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    FV00_REGEX = '.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    RT_PNG_TRANSECT_REGEX = '^unit.*_[0-9]{8}T[0-9]{6}-[0-9]{8}T[0-9]{4}.png$'
    RT_PNG_REGEX = '^unit.*.png$'
    PLATFORM_CODES = {'SG': 'seaglider',
                      'SL': 'slocum_glider'}
    RT_POSITION_SUMMARY = '^unit.*position_summary.txt$'

    @classmethod
    def get_platform(cls, filename):
        """ work out platform type from filename
            DSTG and NRL deployments are slocum glider only
            ANFOG deployments are either seaglider or slocum glider """
        if (re.match(cls.DSTG_REGEX, filename)) or (re.match(cls.NRL_REGEX, filename)):
            platform = 'slocum_glider'
        else:
            fields = cls._get_file_name_fields(filename)
            platform_id = fields[4][:2]
            platform = cls.PLATFORM_CODES[platform_id]

        return platform

    @classmethod
    def get_deployment_code(cls, src_path):
        """Depending on data mode :
           DM :  get deployment code from netcdf global attributes directly
               DSTG : no attribute deployment_code, extract deployment code from title instead
           RT :exctract deployment code from title
        """
        name = os.path.basename(src_path)
        if re.match(cls.DSTG_REGEX, name) or re.match(cls.ANFOG_RT_REGEX, name):
            title = cls._get_nc_att(src_path, 'title')
            deployment_code = title.split()[-1]
            if deployment_code == 'mission':
                raise InvalidFileContentError(
                    "Missing deployment code in {file} ".format(file=name))

        elif re.match(cls.ANFOG_DM_REGEX, name):
            deployment_code = cls._get_nc_att(src_path, 'deployment_code')
        else:
            raise InvalidFileNameError(
                "Invalidfile name {file} ".format(file=name))

        return deployment_code

    @classmethod
    def make_rt_path(cls, path):
        """Convert a Delayed mode path like:
        IMOS/ANFOG/platform/deployment_code/
        in a REALTIME path like :
        IMOS/ANFOG/REALTIME/platform/deployment_code/ """
        try:
            org, facility, platform, deployment_code = path.split('/')
        except ValueError:
            raise ValueError("path '{path}' must have 4 parts".format(path=path))

        rt_path = [org, facility, 'REALTIME', platform, deployment_code]
        return cls._make_path(rt_path)

    @classmethod
    def get_destination(cls, src_path):
        name = os.path.basename(src_path)
        dir_list = []
        fields = cls._get_file_name_fields(name)
        platform = cls.get_platform(name)
        deployment_code = cls.get_deployment_code(src_path)

        if re.match(cls.NRL_REGEX, name):
            project = cls.NRL_BASE
            dir_list.append(project)
        elif re.match(cls.DSTG_REGEX, name):
            project = cls.DSTG_BASE
            dir_list.append(project)
        else:  # IMOS ANFOG RT or DM
            project = fields[0]
            facility = fields[1]
            dir_list.extend([project, facility])
            if re.match(cls.ANFOG_RT_REGEX, name):
                data_type = 'REALTIME'
                dir_list.append(data_type)

        dir_list.extend([platform, deployment_code])

        return cls._make_path(dir_list)
