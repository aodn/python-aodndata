import os
import re

from aodncore.pipeline import HandlerBase, FileType, PipelineFilePublishType
from aodncore.pipeline.exceptions import InvalidFileNameError


class SstaarsHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SstaarsHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def preprocess(self):
        netcdf_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        netcdf_file = netcdf_collection[0]

        if netcdf_file.name == 'SSTAARS.nc' or netcdf_file.name == 'SSTAARS_daily_fit.nc':
            netcdf_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY

    @staticmethod
    def dest_path(filepath):
        sstaars_alt_dir = os.path.join('CSIRO', 'Climatology', 'SSTAARS', '2017')
        sstaars_aodn_dir = os.path.join(sstaars_alt_dir, 'AODN-product')
        netcdf_file_name = os.path.basename(filepath)

        regex_daily_files = re.compile('SSTAARS_daily_fit_[0-9]{3}\.nc')

        if netcdf_file_name == 'SSTAARS.nc':
            return os.path.join(sstaars_alt_dir, netcdf_file_name)
        elif (netcdf_file_name == 'SSTAARS_daily_fit.nc') or re.match(regex_daily_files, netcdf_file_name):
            return os.path.join(sstaars_aodn_dir, netcdf_file_name)
        else:
            raise InvalidFileNameError(
                'invalid file name {filepath}. Not matching \'STAARS.*\.nc\''.format(filepath=filepath))
