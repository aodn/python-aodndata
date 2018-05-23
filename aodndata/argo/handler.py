import os

from aodncore.pipeline import HandlerBase, PipelineFilePublishType


class ArgoHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(ArgoHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.rsync_manifest']

        relative_path_root = os.path.join(self._config.pipeline_config['global']['wip_dir'], 'Argo/dac')
        self.resolve_params = {'relative_path_root': relative_path_root}
        self.include_regexes = ['.*\.nc']

    def preprocess(self):
        """ set NO_ACTION to non NetCDF files"""
        self.file_collection.set_publish_types_from_regexes(addition_type=PipelineFilePublishType.NO_ACTION,
                                                            deletion_type=PipelineFilePublishType.NO_ACTION,
                                                            include_regexes='.*',
                                                            exclude_regexes='.*\.nc')

    def dest_path(self, filepath):
        """The dest_path has already been added to the PipelineFile by the MapManifestResolveRunner, so simply validate
            that the object contains valid dest_path attribute

        :param filepath: filepath for which to retrieve the destination path from the corresponding PipelineFile
        :return: string containing the dest_path attribute of the PipelineFile corresponding with filepath
        """
        rel_path = os.path.relpath(filepath, self.resolve_params['relative_path_root'])
        return os.path.join('IMOS/Argo/dac', rel_path)
