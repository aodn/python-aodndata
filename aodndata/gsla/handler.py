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
                       (?P<product_type>NRT|DM02)\.nc(\.gz)?$
                       """, re.VERBOSE)

GSLA_REGEX_YEARLY = re.compile(r"""
                               IMOS_OceanCurrent_HV_
                               (?P<product_type>|DM01_)  # DM01 yearly file have their product code within the file.
                               (?P<nc_time_cov_start>[0-9]{4})\.nc(\.gz)?$
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
                "Expecting 'product_type' attribute in netCDF'{gzip}'".format(gzip=os.path.basename(netcdf_path))
            )

class GslaHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(GslaHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.gz', '.nc']

    def preprocess(self):

        # if input file is a NetCDF, create a .nc.gz and harvest upload it.
        # historically, files were always sent as *.nc.gz. But as of April 2021, files might be pushed as *.nc.
        # to be consistent, we transform this .nc into a .nz.gz
        if self.file_type is FileType.NETCDF:
            self.file_collection.set_publish_types(PipelineFilePublishType.NO_ACTION)

            gzip_path = os.path.join(self.temp_dir,  self.file_basename + '.gz')
            with open(self.input_file, 'rb') as f_in, gzip.open(gzip_path, 'wb') as gz_out:
                gz_out.writelines(f_in)

            # publish
            self.add_to_collection(gzip_path, publish_type=PipelineFilePublishType.HARVEST_UPLOAD)

        if self.file_type is FileType.GZIP:
            # add nc_gz file to collection (not by default)
            self.file_collection.add(self.input_file_object)
            netcdf_file_gz_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)
            netcdf_file_gz = netcdf_file_gz_collection[0]
            netcdf_file_gz.publish_type = PipelineFilePublishType.HARVEST_UPLOAD  # default

            # some GSLA files are gzipped, so gunzip them before checking them
            # if uploaded file is GZIP check that GZIP contains a NetCDF
            netcdf_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
            if len(netcdf_collection) != 1:
                raise InvalidInputFileError(
                    "Expecting one netCDF file in GZIP archive '{gzip}'".format(gzip=os.path.basename(self.input_file))
                )

        netcdf_file_gz = self.file_collection.filter_by_attribute_id('file_type', FileType.GZIP)[0]
        netcdf_file = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)[0]
        # setting the path of the gz file with the gunzipped file
        netcdf_file_gz.dest_path = self.dest_path(netcdf_file.src_path)
        # Nothing to do with *.nc. Talend can harvest *.nc.gz. Set to NO_ACTION
        netcdf_file.publish_type = PipelineFilePublishType.NO_ACTION

        """ default values
        by default we push to the storage the file landed in the pipeline (ie *.nc.gz) """
        push_new_file = True
        remove_previous_version = False

        if push_new_file:
            if GSLA_REGEX_YEARLY.match(netcdf_file.name):
                # yearly file should never be harvested
                netcdf_file_gz.publish_type = PipelineFilePublishType.UPLOAD_ONLY
        else:
            raise InvalidFileNameError("file name: \"{filename}\"  creation date is older than file already on "
                                       "storage".format(filename=netcdf_file_gz.name))

    @staticmethod
    def dest_path(filepath):
        " Netcdf only as an input. Not nc.gz"
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

        # destination path should always be for nc.gz files. So we force it
        return '{val}.gz'.format(val=dest_path_val) if dest_path_val.endswith('.nc') else dest_path_val

