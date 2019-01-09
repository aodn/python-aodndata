import datetime
import os
import re

from netCDF4 import Dataset
from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType


class SoopTrvHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopTrvHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def preprocess(self):
        """
        Files to be deleted as found in 'soop_trv_duplicate_ls' wfs layer
        """
        files_to_delete = self.state_query.query_wfs_urls_for_layer('soop_trv_duplicate_ls')

        for f in files_to_delete:
            file_to_delete = PipelineFile(os.path.basename(f),
                                          is_deletion=True,
                                          dest_path=f,
                                          file_update_callback=self._file_update_callback
                                          )
            file_to_delete.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
            self.file_collection.add(file_to_delete)

    def get_main_soop_trv_var(self, filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        variables = netcdf_file_obj.variables.keys()
        netcdf_file_obj.close()

        if 'CPHL' in variables:
            return 'CPHL'
        elif 'TEMP' in variables:
            return 'TEMP'
        elif 'PSAL' in variables:
            return 'PSAL'
        elif 'TURB' in variables:
            return 'TURB'

    def get_main_var_folder_name(self, filepath):
        main_var = self.get_main_soop_trv_var(filepath)

        if main_var == 'CPHL':
            return 'chlorophyll'
        elif main_var == 'TEMP':
            return 'temperature'
        elif main_var == 'PSAL':
            return 'salinity'
        elif main_var == 'TURB':
            return 'turbidity'

    def remove_creation_date_from_filename(self, filepath):
        return re.sub('_C-.*$', '.nc', filepath)

    def dest_path(self, filepath):
        netcdf_file_obj = Dataset(filepath, mode='r')
        ship_code = netcdf_file_obj.platform_code
        vessel_name = netcdf_file_obj.vessel_name
        main_var_folder = self.get_main_var_folder_name(filepath)

        date_start = datetime.datetime.strptime(netcdf_file_obj.time_coverage_start, "%Y-%m-%dT%H:%M:%SZ")
        date_start = date_start.strftime('%Y%m%dT%H%M%SZ')
        date_end = datetime.datetime.strptime(netcdf_file_obj.time_coverage_end, "%Y-%m-%dT%H:%M:%SZ")
        date_end = date_end.strftime('%Y%m%dT%H%M%SZ')

        netcdf_filename = self.remove_creation_date_from_filename(os.path.basename(filepath))
        relative_netcdf_path = os.path.join('IMOS', 'SOOP', 'SOOP-TRV', '%s_%s' % (ship_code, vessel_name), 'By_Cruise',
                                            'Cruise_START-%s_END-%s' % (date_start, date_end), main_var_folder,
                                            netcdf_filename)

        netcdf_file_obj.close()
        return relative_netcdf_path
