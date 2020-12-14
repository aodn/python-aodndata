import os
import re

from aodncore.pipeline import HandlerBase, PipelineFilePublishType


class SrsOcBodBawHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsOcBodBawHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.png', '.csv']

    def preprocess(self):
        for f in self.file_collection:
            if f.extension != '.nc':
                f.publish_type = PipelineFilePublishType.UPLOAD_ONLY

    @staticmethod
    def remove_creation_date_from_filename(filepath):
        return re.sub('_C-.*.(csv|png|nc)$', os.path.splitext(filepath)[1], filepath)

    def dest_path(self, filepath):
        bodbaw_dir = os.path.join('IMOS', 'SRS', 'OC', 'BODBAW')

        filename = os.path.basename(self.remove_creation_date_from_filename(filepath))
        m = re.search(
            r'^IMOS_SRS-OC-BODBAW_X_([0-9]+T[0-9]+Z)_(.*)-(suspended_matter|pigment|backscattering|absorption).*_END-([0-9]+T[0-9]+Z)\.(nc|csv|png)$',
            filename)
        if m is None:
            raise ValueError("file name not matching regex to deduce dest_path")

        product_type = m.group(3)
        if 'absorption' in product_type:
            product_type = 'absorption'

        cruise_id = m.group(2).split('-')[0]  # split to get rid of the station_code within the cruise_id if exists

        return os.path.join(bodbaw_dir, '{cruise}'.format(cruise=cruise_id),
                            product_type, filename)
