import os
import re

from aodncore.pipeline import HandlerBase


class SrsOcLjcoHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsOcLjcoHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    def remove_creation_date_from_filename(self, filepath):
        return re.sub('_C-.*.nc$', '.nc', filepath)

    def dest_path(self, filepath):
        ljco_wqm_dir = os.path.join('IMOS', 'SRS', 'OC', 'LJCO')

        netcdf_filename = os.path.basename(filepath)
        netcdf_filename = self.remove_creation_date_from_filename(netcdf_filename)

        # looking for product_name
        m = re.search('^IMOS_SRS-OC-LJCO_(.*)_(.*)_SRC_FV(.*)\.nc$',
                      netcdf_filename)

        if m is None:
            raise ValueError("file name not matching regex to deduce dest_path")

        product_type_ls = re.compile('ACS|EcoTriplet|BB9|HyperOCR|WQM')
        product_type_netcdf = product_type_ls.findall(netcdf_filename)

        product_temp_ls = re.compile('hourly|daily|monthly')
        product_temp_netcdf = product_temp_ls.findall(netcdf_filename)

        if product_type_netcdf == [] or product_temp_netcdf == []:
            raise ValueError("can not find matching instrument or time coverage from filename")
        product_dir = '%s-%s' % (product_type_netcdf[0], product_temp_netcdf[0])

        year = int(m.group(2)[0:4])
        if 'hourly' in product_dir:
            month = int(m.group(2)[4:6])
            day = int(m.group(2)[6:8])
            relative_netcdf_path = os.path.join(ljco_wqm_dir, product_dir, '%d' % year,
                                                '%02d' % month, '%02d' % day, netcdf_filename)
        else:
            relative_netcdf_path = os.path.join(ljco_wqm_dir, product_dir, str(year),
                                                netcdf_filename)

        return relative_netcdf_path
