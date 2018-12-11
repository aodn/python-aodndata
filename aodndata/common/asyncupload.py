from __future__ import absolute_import
from __future__ import unicode_literals
from aodncore.pipeline import HandlerBase, PipelineFilePublishType


class AsyncUploadHandler(HandlerBase):
    """Implement the async upload utility as an "upload only" handler class
    """

    def __init__(self, *args, **kwargs):
        super(AsyncUploadHandler, self).__init__(*args, **kwargs)
        self.default_addition_publish_type = PipelineFilePublishType.UPLOAD_ONLY
        self.default_deletion_publish_type = PipelineFilePublishType.NO_ACTION

        self.allowed_extensions = ['.map_manifest']

    def dest_path(self, filepath):
        """The dest_path has already been added to the PipelineFile by the MapManifestResolveRunner, so simply validate
            that the object contains valid dest_path attribute

        :param filepath: filepath for which to retrieve the destination path from the corresponding PipelineFile
        :return: string containing the dest_path attribute of the PipelineFile corresponding with filepath
        """
        pipelinefile = self.file_collection.get_pipelinefile_from_src_path(filepath)
        try:
            dest_path = pipelinefile.dest_path
        except AttributeError:
            raise AttributeError("PipelineFile for path '{filepath}' not found in collection".format(filepath=filepath))
        else:
            return dest_path
