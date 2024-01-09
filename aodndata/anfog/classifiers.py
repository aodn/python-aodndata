import os
import re

from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidFileNameError


class AnfogFileClassifier(FileClassifier):
    MISSION_LISTING = 'HarvestmissionList.csv'
    ANFOG_BASE = 'IMOS/ANFOG'
    ANFOG_RT_REGEX = \
        '^IMOS_ANFOG_([^R]+)_[0-9]{8}T[0-9]{6}Z_.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    RT_POSITION_SUMMARY = '.*position_summary.txt$'
    RT_PNG_TRANSECT_REGEX = '.*_[0-9]{8}T[0-9]{6}-[0-9]{8}T[0-9]{6}.png$'
    RT_PNG_REGEX = '.*.png$'
    ANFOG_DM_REGEX = \
        '^IMOS_ANFOG.*_[0-9]{8}T[0-9]{6}Z.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    ANFOG_NC_REGEX = \
        '^IMOS_ANFOG_([^R]+)_.*[0-9]{8}T[0-9]{6}Z.*_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_REGEX = '^DSTO_.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_RAW = '^DSTO_.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_BASE = 'Department_of_Defence/DSTG'
    ADAPTER_REGEX = '^IMOS_UWA_.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    ADAPTER_BASE = 'UWA'
    DM_REGEX = '%s|%s|%s' % (ANFOG_DM_REGEX, DSTG_REGEX, ADAPTER_REGEX)
    RAW_DATA_REGEX = '^IMOS_.*R.*_[0-9]{8}T[0-9]{6}Z_.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    RAW_BATTERY_REGEX = '^ANFOG_E_[0-9]{8}T[0-9]{6}Z_.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    RAW_FILES_REGEX = '%s|%s|%s|%s|%s' % ('.*rawfiles.zip$', '.*rawfiles.rar$',
                                          RAW_DATA_REGEX, RAW_BATTERY_REGEX, DSTG_RAW)
    PLATFORM_CODES = {'SG': 'seaglider',
                      'SL': 'slocum_glider',
                      'RU': 'slocum_glider'
                      }
    UPLOAD_TO_S3_REGEX = '.*(.kml|.jpg|.pdf|.txt)$'

    @classmethod
    def get_platform(cls, filename):
        """ work out platform type from filename
            DSTG and NRL deployments are slocum glider only
            ANFOG deployments are either seaglider or slocum glider """
        if (re.match(cls.DSTG_REGEX, filename)) or (re.match(cls.ADAPTER_REGEX, filename)):
            platform = 'slocum_glider'
        elif (re.match(cls.ANFOG_DM_REGEX, filename)) or (re.match(cls.ANFOG_RT_REGEX, filename)):
            fields = cls._get_file_name_fields(filename)
            platform_id = fields[4][:2]
            platform = cls.PLATFORM_CODES[platform_id]
        else:  # status text file
            platform_id = filename.split('-')[0]
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

        elif re.match(cls.ANFOG_NC_REGEX, name) or re.match(cls.ADAPTER_REGEX, name):
            deployment_code = cls._get_nc_att(src_path, 'deployment_code')
        elif name.endswith('.txt'):
            # extract deployment code from filename like SL-Yamba20180609_completed.txt
            field = name.split('_')
            deployment_code = field[0].split('-')[1]
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
        """set destination path
           hadnle also special case """
        name = os.path.basename(src_path)
        dir_list = []
        if name.endswith('.txt'):
            [deployment, message] = cls._get_file_name_fields(name, min_fields=2)
            platform = cls.PLATFORM_CODES[deployment.split('-')[0]]
            deployment_code = deployment.split('-')[1]
        else:
            platform = cls.get_platform(name)
            deployment_code = cls.get_deployment_code(src_path)

        if re.match(cls.ADAPTER_REGEX, name):
            dir_list.append(cls.ADAPTER_BASE)
        elif re.match(cls.DSTG_REGEX, name):
            dir_list.append(cls.DSTG_BASE)
        else:  # IMOS ANFOG RT, DM, or status text file
            dir_list.append(cls.ANFOG_BASE)
            if re.match(cls.ANFOG_RT_REGEX, name) or name.endswith('.txt'):
                data_type = 'REALTIME'
                dir_list.append(data_type)

        dir_list.extend([platform, deployment_code])

        return cls._make_path(dir_list)
