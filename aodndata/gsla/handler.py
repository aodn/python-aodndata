import gzip
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
                       (?P<product_type>NRT|DM0[1-2])\.nc$
                       """, re.VERBOSE)

GSLA_REGEX_YEARLY = re.compile(r"""
                               IMOS_OceanCurrent_HV_
                               (?P<product_type>|DM01_)  # DM01 yearly file have their product code within the file.
                               (?P<nc_time_cov_start>[0-9]{4})\.nc$
                               """, re.VERBOSE)


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
                "Expecting 'product_type' attribute in netCDF'{ncfile}'".format(ncfile=os.path.basename(netcdf_path))
            )

class GslaHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(GslaHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def preprocess(self):

        # historically, files were always sent as *.nc.gz. As of April 2021, files could be pushed as *.nc as well.
        # from March 2023, as part of the whole collection reprocessing, files will be pushed only as *.nc

        netcdf_file_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        netcdf_file = netcdf_file_collection[0]

        # RT and DM NetCDF files to be harvested
        if GSLA_REGEX.match(netcdf_file.name):
            netcdf_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD

        # Yearly file should never be harvested, upload only
        if GSLA_REGEX_YEARLY.match(netcdf_file.name):
            netcdf_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY

    @staticmethod
    def dest_path(filepath):
        " Netcdf only as an input"
        file_basename = os.path.basename(filepath)
        gsla_type = get_gsla_type(filepath)
        # the facility does not want the version number in the directory name anymore
        if "DM" in gsla_type:
            gsla_type = "DM"

        if GSLA_REGEX_YEARLY.match(file_basename):
            dest_path_val = os.path.join(GSLA_PREFIX_PATH, "DM/yearfiles", file_basename)

        else:
            fields = get_pattern_subgroups_from_string(file_basename, GSLA_REGEX)
            gsla_year = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ').year
            dest_path_val = os.path.join(GSLA_PREFIX_PATH, gsla_type, str(gsla_year), file_basename)

        return '{val}'.format(val=dest_path_val)
