import os
import re
from datetime import datetime

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
            '^IMOS_SRS-OC-BODBAW_X_([0-9]+T[0-9]+Z)_(.*)-(suspended_matter|pigment|backscattering|absorption).*_END-([0-9]+T[0-9]+Z)\.(nc|csv|png)$',
            filename)
        if m is None:
            raise ValueError("file name not matching regex to deduce dest_path")

        product_type = m.group(3)
        if 'absorption' in product_type:
            product_type = 'absorption'

        cruise_id = m.group(2)
        year = datetime.strptime(m.group(1), '%Y%m%dT%H%M%SZ').strftime("%Y")

        return os.path.join(bodbaw_dir, '{year}_cruise-{cruise}'.format(year=year, cruise=cruise_id),
                            product_type, filename)
