import os

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType


class ArgoHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(ArgoHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.rsync_manifest']

        relative_path_root = os.path.join(self._config.pipeline_config['global']['wip_dir'], 'Argo/dac')
        self.resolve_params = {'relative_path_root': relative_path_root}
        self.include_regexes = [r'.*\.nc']
        self.lockfile_path = os.path.join(os.path.dirname(self.input_file), 'argo.lock')  # argo.lock in $INCOMING_DIR/Argo

    def preprocess(self):
        """ set NO_ACTION to non NetCDF files"""
        self.file_collection. \
            filter_by_attribute_id_not('file_type', FileType.NETCDF). \
            set_publish_types(PipelineFilePublishType.NO_ACTION)

        # creating a lock file in the incoming dir which the rsync script (from data-services) will check for existence
        with open(self.lockfile_path, 'w') as fp:
            pass

    def postprocess(self):
        """
        delete argo.lock from $INCOMING_DIR preventing new rsync
        :return:
        """
        if os.path.exists(self.lockfile_path):
            os.remove(self.lockfile_path)


    def dest_path(self, filepath):
        """The dest_path has already been added to the PipelineFile by the MapManifestResolveRunner, so simply validate
            that the object contains valid dest_path attribute

        :param filepath: filepath for which to retrieve the destination path from the corresponding PipelineFile
        :return: string containing the dest_path attribute of the PipelineFile corresponding with filepath
        """
        rel_path = os.path.relpath(filepath, self.resolve_params['relative_path_root'])
        return os.path.join('IMOS/Argo/dac', rel_path)
