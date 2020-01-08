import os
import re
from datetime import datetime

from aodncore.pipeline import HandlerBase, FileType, PipelineFilePublishType, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidInputFileError
from aodncore.util.misc import get_pattern_subgroups_from_string
from netCDF4 import Dataset

GSLA_PREFIX_PATH = "IMOS/OceanCurrent/GSLA"

GSLA_REGEX = re.compile(r"""
                       IMOS_OceanCurrent_HV_
                       (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_GSLA_FV02_
                       (?P<product_type>NRT00|DM00|DM01)_C-
                       (?P<creation_date>[0-9]{8}T[0-9]{6}Z)\.nc(\.gz)?$
                       """, re.VERBOSE)

GSLA_REGEX_YEARLY = re.compile(r"""
                               IMOS_OceanCurrent_HV_
                               (?P<nc_time_cov_start>[0-9]{4})_C-
                               (?P<creation_date>[0-9]{8}T[0-9]{6}Z)\.nc(\.gz)?$
                               """, re.VERBOSE)


def get_creation_date(filepath):
    """ :return: creation date    """
    file_basename = os.path.basename(filepath)
    if GSLA_REGEX.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, GSLA_REGEX)

    elif GSLA_REGEX_YEARLY.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, GSLA_REGEX_YEARLY)

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce creation_date".format(
                filename=file_basename))

    return datetime.strptime(fields['creation_date'], '%Y%m%dT%H%M%SZ')


def get_gsla_type(filepath):
    """ :return:  gsla file type """
    file_basename = os.path.basename(filepath)
    if GSLA_REGEX.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, GSLA_REGEX)
        return fields['product_type']

    elif GSLA_REGEX_YEARLY.match(file_basename):
        return os.path.join(get_product_type(filepath), 'yearfiles')

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=file_basename))


def get_product_type(netcdf_path):
    with Dataset(netcdf_path, mode='r') as nc_obj:
        try:
            return nc_obj.product_type
        except AttributeError:
            raise InvalidInputFileError(
                "Expecting 'product_type' attribute in netCDF'{gzip}'".format(gzip=os.path.basename(netcdf_path))
            )


class GslaHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(GslaHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.gz']

    def preprocess(self):
        # add nc_gz file to collection (not by default)
        self.file_collection.add(self.input_file_object)
        netcdf_file_gz_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)
        netcdf_file_gz = netcdf_file_gz_collection[0]
        netcdf_file_gz.publish_type = PipelineFilePublishType.HARVEST_UPLOAD  # default

        # GSLA files are gzipped, so gunzip them before checking them
        if self.file_type is FileType.GZIP:
            # if uploaded file is GZIP check that GZIP contains a NetCDF
            netcdf_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
            if len(netcdf_collection) != 1:
                raise InvalidInputFileError(
                    "Expecting one netCDF file in GZIP archive '{gzip}'".format(gzip=os.path.basename(self.input_file))
                )

            netcdf_file = netcdf_collection[0]
            # setting the path of the gz file with the gunzipped file
            netcdf_file_gz.dest_path = self.dest_path(netcdf_file.src_path)
            # Nothing to do with *.nc. Talend can harvest *.nc.gz. Set to NO_ACTION
            netcdf_file.publish_type = PipelineFilePublishType.NO_ACTION

            # we don't know the product type (DM00 or DM01) of the file already
            # on s3 in order to deduce its path. We need to get the product
            # type from the file in incoming
            result_previous_version_creation_date = self.get_previous_version_creation_date(netcdf_file.src_path)

            """ default values
            by default we push to the storage the file landed in the pipeline (ie *.nc.gz) """
            push_new_file = True
            remove_previous_version = False

            # compare creation dates with file already on storage
            if result_previous_version_creation_date:
                new_file_creation_date = get_creation_date(netcdf_file.name)
                if result_previous_version_creation_date > new_file_creation_date:
                    push_new_file = False
                elif result_previous_version_creation_date == new_file_creation_date:
                    push_new_file = True
                else:
                    remove_previous_version = True
                    previous_file_path = self.get_previous_version_object(netcdf_file.src_path)

            if push_new_file:
                if GSLA_REGEX_YEARLY.match(netcdf_file.name):
                    # yearly file should never be harvested
                    netcdf_file_gz.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            else:
                raise InvalidFileNameError("file name: \"{filename}\"  creation date is older than file already on "
                                           "storage".format(filename=netcdf_file_gz.name))

            # deletion of the previous file
            if remove_previous_version:
                previous_file_name = os.path.basename(previous_file_path)
                file_to_delete = PipelineFile(previous_file_name,
                                              is_deletion=True,
                                              dest_path=previous_file_path,
                                              file_update_callback=self._file_update_callback
                                              )

                if GSLA_REGEX_YEARLY.match(netcdf_file.name):
                    file_to_delete.publish_type = PipelineFilePublishType.DELETE_ONLY
                else:
                    file_to_delete.publish_type = PipelineFilePublishType.DELETE_UNHARVEST

                self.file_collection.add(file_to_delete)

    def get_previous_version_object(self, filepath):
        destination = self.dest_path(filepath)
        destination_no_creation_date = re.sub('_C-[0-9]{8}T[0-9]{6}Z.*$', '', destination)

        res = self.state_query.query_storage(destination_no_creation_date).keys()
        if len(res) > 1:
            raise RuntimeError('More than 1 previous version of {filename} was found on storage.'.
                               format(filename=os.path.basename(filepath)))
        elif len(res) == 1:
            return list(res)[0]
        else:
            return False

    def get_previous_version_creation_date(self, filepath):
        """
        find matching old netcdf_file.gz object already on s3 by stripping the creation date of the new file object path
        :return: old creation date if exists
                 returns None if no previous file was found
        """
        prev = self.get_previous_version_object(filepath)
        if prev:
            return get_creation_date(prev)

    @staticmethod
    def dest_path(filepath):
        " Netcdf only as an input. Not nc.gz"
        file_basename = os.path.basename(filepath)
        gsla_type = get_gsla_type(filepath)

        if GSLA_REGEX_YEARLY.match(file_basename):
            dest_path_val = os.path.join(GSLA_PREFIX_PATH, gsla_type, file_basename)

        else:
            fields = get_pattern_subgroups_from_string(file_basename, GSLA_REGEX)
            gsla_year = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ').year
            dest_path_val = os.path.join(GSLA_PREFIX_PATH, gsla_type, str(gsla_year), file_basename)

        # destination path should always be for nc.gz files. So we force it
        return '{val}.gz'.format(val=dest_path_val) if dest_path_val.endswith('.nc') else dest_path_val

