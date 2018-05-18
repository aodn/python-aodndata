import os
import re

from aodncore.pipeline import FileClassifier, PipelineFileCheckType, PipelineFilePublishType, FileType
from aodncore.pipeline.exceptions import InvalidFileContentError, InvalidInputFileError, InvalidFileNameError


class AnfogFileClassifier(FileClassifier):
    MISSION_LISTING = 'HarvestmissionList.csv'
    ANFOG_RT_REGEX = \
        '^IMOS_ANFOG.*_[0-9]{8}T[0-9]{6}Z_.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    ANFOG_DM_REGEX = \
        '^IMOS_ANFOG.*_[0-9]{8}T[0-9]{6}Z.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_REGEX = '^DSTO_.*_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    DSTG_BASE = 'Department_of_Defence'
    NRL_REGEX = '^NRL_.*_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    NRL_BASE = 'US_Naval_Research_Laboratory'
    DM_REGEX = '.*_FV01_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    FV00_REGEX = '.*_FV00_timeseries_END-[0-9]{8}T[0-9]{6}Z.nc$'
    RT_PNG_TRANSECT_REGEX = '.*_[0-9]{8}T[0-9]{6}-[0-9]{8}T[0-9]{4}.png$'
    PLATFORM_CODES = {'SG': 'seaglider',
                      'SL': 'slocum_glider'}

    @classmethod
    def set_data_mode(cls, handler):
        """Based on ZIP content, define the data mode - DM or RT
            - DM : netcdf file is FV01
            - RT : FV00, images (unit???_*.png) and *position_summary.txt
        """
        netcdf = handler.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        if not netcdf:
            raise InvalidInputFileError(
                "Expecting one NetCDF file in ZIP archive '{zip}'".format(zip=os.path.basename(handler.input_file))
            )

        for f in netcdf:
            if re.match(cls.DM_REGEX, f.name):
                return 'DM'
            else:
                # Check that zip content is RT material by looking for .png or position_summary.txt file
                png = handler.file_collection.filter_by_attribute_value('extension', 'png')
                position_txtfile = handler.file_collection.filter_by_attribute_regex('name', '.*position_summary.txt$')
                if (png is not None) or (position_txtfile is not None):
                    return 'RT'
                else:
                    raise InvalidFileContentError(
                        "Missing ancillary files in ZIP archive {name}".format(
                            name=os.path.basename(handler.input_file)))

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
    def get_deployment_code(cls, src_file):
        """Depending on data mode :
           DM :  get deployment code from netcdf global attributes directly
               DSTG : no attribute deployment_code, extract deployment code from title instead
           RT :exctract deployment code from title
        """
        if re.match(cls.DSTG_REGEX, src_file.name) or re.match(cls.ANFOG_RT_REGEX, src_file.name):
            title = cls._get_nc_att(src_file.src_path, 'title')
            deployment_code = title.split()[-1]
            if deployment_code == 'mission':
                raise InvalidFileContentError(
                    "Missing deployment code in {file} ".format(file=os.path.basename(src_file.name)))

        elif re.match(cls.ANFOG_DM_REGEX, src_file.name):
            deployment_code = cls._get_nc_att(src_file.src_path, 'deployment_code')
        else:
            raise InvalidFileNameError(
                "Invalidfile name {file} ".format(file=os.path.basename(src_file.name)))

        return deployment_code

    @classmethod
    def set_attributes_per_file_type(cls, filecollection, destination, path):
        """
        Set check_type,publish_type and dest_path or archive_path attribute
           to a collection of file of the same type/format according to its destination
           destination is either 'S3upload' or 'archive'
        """
        for f in filecollection:
            f.check_type = PipelineFileCheckType.FORMAT_CHECK
            if destination == 'S3upload':
                f.publish_type = PipelineFilePublishType.UPLOAD_ONLY
                f.dest_path = os.path.join(path, f.name)
            elif destination == 'archive':
                f.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
                f.archive_path = os.path.join(path, f.name)

    @classmethod
    def dest_path(cls, src_file, data_mode):
        dir_list = []
        fields = cls._get_file_name_fields(src_file.name)
        platform = cls.get_platform(src_file.name)
        deployment_code = cls.get_deployment_code(src_file)

        if fields[0] == 'NRL':
            project = cls.NRL_BASE
            dir_list.extend([project])
        elif fields[0] == 'DSTO':
            project = cls.DSTG_BASE
            facility = 'DSTG'
            dir_list.extend([project, facility])
        else:  # IMOS ANFOG
            project = fields[0]
            facility = fields[1]
            dir_list.extend([project, facility])

        if data_mode == 'RT':
            data_type = 'REALTIME'
            dir_list.append(data_type)

        dir_list.extend([platform, deployment_code])

        return cls._make_path(dir_list)
