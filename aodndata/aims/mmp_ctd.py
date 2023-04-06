import os
from datetime import datetime

from aodncore.pipeline import HandlerBase, FileType, PipelineFilePublishType
from netCDF4 import Dataset

"""
Processing MMP CTD data from AIMS
"""



class MmpCtdHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(MmpCtdHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def preprocess(self):
        netcdf_collection = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        netcdf_file = netcdf_collection[0]

        if netcdf_file.name.endswith('.nc'):
            netcdf_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD

    @staticmethod
    def dest_path(filepath):
        nc_obj = Dataset(filepath, mode='r')
        year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y")

        return os.path.join('AIMS', 'Marine_Monitoring_Program', 'CTD_profiles',
                            year, os.path.basename(filepath))
