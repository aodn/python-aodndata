import os

from aodncore.pipeline import HandlerBase, PipelineFilePublishType


class AuvHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(AuvHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.manifest', '.csv', '.dir_manifest']
        self.resolve_params = {'relative_path_root': os.path.join(self._config.pipeline_config['global']['wip_dir'])}

        if self.input_file.endswith('.dir_manifest') or self.input_file.endswith('images.manifest'):
            self.default_addition_publish_type = PipelineFilePublishType.UPLOAD_ONLY

    # manifest filename gives us the following info [campaign_name]-[dive_name].[manifest_type].manifest
    def get_campaign_name(self):
        return os.path.basename(self.input_file).split('-')[0]

    def get_dive_name(self):
        return os.path.basename(self.input_file).split('-')[1].split('.')[0]

    def manifest_type(self):
        # 0 is the main dive name, 1 the manifest type, 2 is manifest
        return os.path.basename(self.input_file).split('.')[1]

    def dest_path(self, filepath):
        """The dest_path has already been added to the PipelineFile by the MapManifestResolveRunner, so simply validate
            that the object contains valid dest_path attribute

        :param filepath: filepath for which to retrieve the destination path from the corresponding PipelineFile
        :return: string containing the dest_path attribute of the PipelineFile corresponding with filepath
        """

        if self.manifest_type() == 'images':
            rel_path = filepath.split("AUV/AUV_VIEWER_PROCESSING/thumbnails/", 1)[1]
            return os.path.join('IMOS/AUV/auv_viewer_data/images', rel_path)
        elif self.manifest_type() == 'csv':
            return os.path.join('IMOS/AUV/auv_viewer_data/csv_outputs', self.get_campaign_name(),
                                os.path.basename(filepath))
        elif self.manifest_type() == 'netcdf':
            return os.path.join('IMOS/AUV', self.get_campaign_name(), self.get_dive_name(), 'hydro_netcdf',
                                os.path.basename(filepath))
        elif self.manifest_type() == 'dive' or self.manifest_type() == 'pdfreports':
            rel_path = filepath.split("AUV/AUV_DOWNLOAD_CAMPAIGN/", 1)[1]
            return os.path.join('IMOS/AUV', rel_path)
