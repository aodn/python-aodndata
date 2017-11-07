import os

from aodncore.pipeline import HandlerBase


class SoopXbtNrtHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopXbtNrtHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.manifest']

    def dest_path(self, filepath):
        """The dest_path has already been added to the PipelineFile by the MapManifestResolveRunner, so simply validate
            that the object contains valid dest_path attribute

        :param filepath: filepath for which to retrieve the destination path from the corresponding PipelineFile
        :return: string containing the dest_path attribute of the PipelineFile corresponding with filepath
        """
        rel_path = filepath.split("sbddata/", 1)[1]
        return os.path.join('IMOS/SOOP/SOOP-XBT/REALTIME', rel_path)
