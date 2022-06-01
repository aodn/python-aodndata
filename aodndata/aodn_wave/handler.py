import os
import re

from netCDF4 import Dataset

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileContentError
from aodndata.aodn_wave.classifiers import AodnWaveFileClassifier

class AodnWaveHandler(HandlerBase):
    """Handling AODN wave data files in Near Realtime or Delayed mode. It handles the following types of NetCDF files:
     * Integral wave parameters data files in Delayed mode and Near Realtime, which are harvested;
     * Spectral data files only in Delayed mode, which are just uploaded to S3;
     * Raw displacement data files only in Delayed mode, which are just uploaded to S3.
    """

    def __init__(self, *args, **kwargs):
        super(AodnWaveHandler, self).__init__(*args, **kwargs)

    def process_wave_files(self, input_file):
        """
        Set integral wave parameters delayed mode and realtime files destination path based on file attributes
         files have to be uploaded to S3 and are not harvested
        """
        input_file = AodnWaveFileClassifier.get_data_type(input_file)
        if AodnWaveFileClassifier.get_data_type.datatype == 'WAVE-PARAMETERS':
            input_file.publish_type = PipelineFilePublishType.HARVEST_ONLY
        else:
            input_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY

