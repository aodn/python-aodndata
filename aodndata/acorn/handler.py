import os
import re
from datetime import datetime
from netCDF4 import Dataset

from aodncore.pipeline import HandlerBase, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError, MissingConfigParameterError
from aodncore.util.misc import get_pattern_subgroups_from_string

FILE_TYPE_NEED_INDEX = ('radial', 'radial_quality_controlled', 'gridded_1h-avg-current-map_non-QC',
                        'gridded_1h-avg-current-map_QC', 'gridded_1h-avg-wind-map_QC',
                        'gridded_1h-avg-wave-site-map_QC')

ACORN_FILE_PATTERN = re.compile(r"""
                                ^IMOS_ACORN_
                                (?P<data_parameter_code>[A-Z].*)_
                                (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                                (?P<platform_code>[A-Z]{3,4})_
                                (?P<file_version>FV0[0-1])_
                                (?P<product_type>.*)
                                \.nc$
                                """, re.VERBOSE)


def get_type(filepath):
    """return acorn_file_type, the file type of an ACORN file based on its filename"""
    file_basename = os.path.basename(filepath)
    unknown_product = False
    if ACORN_FILE_PATTERN.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, ACORN_FILE_PATTERN)
        product_type = fields['product_type']
        file_version = fields['file_version']
        platform_code = fields['platform_code']

        if product_type == 'radial' and file_version == 'FV00':
            acorn_file_type = "radial"

        elif product_type == 'radial' and file_version == 'FV01':
            acorn_file_type = "radial_quality_controlled"

        elif product_type == 'sea-state' and file_version == 'FV00':
            acorn_file_type = "vector"

        elif product_type == 'wavespec' and file_version == 'FV01':
            acorn_file_type = "gridded_1h-avg-wave-spectra_QC"

        elif product_type == 'windp' and file_version == 'FV01':
            acorn_file_type = "gridded_1h-avg-wind-map_QC"

        elif product_type == 'wavep' and file_version == 'FV01':
            site_map_station = ['CBG', 'SAG', 'ROT', 'COF']

            if any(s == platform_code for s in site_map_station):
                acorn_file_type = "gridded_1h-avg-wave-site-map_QC"
            else:
                acorn_file_type = "gridded_1h-avg-wave-station-map_QC"

        elif product_type == '1-hour-avg' and file_version == 'FV00':
            acorn_file_type = "gridded_1h-avg-current-map_non-QC"

        elif product_type == '1-hour-avg' and file_version == 'FV01':
            acorn_file_type = "gridded_1h-avg-current-map_QC"

        else:
            unknown_product = True
    else:
        unknown_product = True

    if unknown_product:
        raise InvalidFileNameError("file name: \"{filename}\" Unknown product type from filename".
                                   format(filename=file_basename))

    return acorn_file_type


def get_creation_date(netcdf_path):
    with Dataset(netcdf_path, mode='r') as nc_obj:
        nc_pipeline_date_created_str = nc_obj.date_created
        nc_pipeline_date_created = datetime.strptime(nc_pipeline_date_created_str, '%Y-%m-%dT%H:%M:%SZ')
    return nc_pipeline_date_created


class AcornHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(AcornHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

        try:
            self.opendap_root = self.config.pipeline_config['global']['opendap_root']
        except KeyError:
            raise MissingConfigParameterError("missing required config item 'opendap_root' in the pipeline config")

    def preprocess(self):
        nc_file = self.file_collection[0]

        # if file contains any of FILE_TYPE_NEED_INDEX, we index, otherwise publish only
        if any(s in get_type(nc_file.name) for s in FILE_TYPE_NEED_INDEX):
            nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
        else:
            nc_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY

        # check if file with same dest_path already on s3. If yes, check its date_created nc attribute to know
        # if we need to overwrite this object or not
        destination_s3 = self.dest_path(nc_file.name)

        storage_query_res = self.state_query.query_storage(destination_s3).keys()

        # creation date of the new file in the pipeline
        if destination_s3 in storage_query_res:
            creation_date_nc_pipeline = get_creation_date(nc_file.src_path)

            # creation date of the file already published
            creation_date_nc_s3 = get_creation_date(os.path.join(self.opendap_root, destination_s3))

            if creation_date_nc_pipeline < creation_date_nc_s3:
                raise InvalidFileContentError("file name: \"{filename}\"  creation date is older than file already on storage".
                                           format(filename=nc_file.name))

    @staticmethod
    def dest_path(filepath):
        file_basename = os.path.basename(filepath)
        file_type = get_type(filepath)

        fields = get_pattern_subgroups_from_string(file_basename, ACORN_FILE_PATTERN)
        nc_time_cov_start = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ')

        return os.path.join('IMOS', 'ACORN', file_type, fields['platform_code'],
                            '%d' % nc_time_cov_start.year, '%02d' % nc_time_cov_start.month,
                            '%02d' % nc_time_cov_start.day,
                            file_basename
                            )
