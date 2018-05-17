import os
import re

from aodncore.pipeline import HandlerBase
from aodncore.pipeline.exceptions import InvalidFileNameError
from datetime import datetime


class SrsOcLjcoHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsOcLjcoHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc']

    @staticmethod
    def dest_path(filepath):
        ljco_s3_base_dir = os.path.join('IMOS', 'SRS', 'OC', 'LJCO')

        netcdf_filename = os.path.basename(filepath)
        netcdf_filename = re.sub('_C-.*.nc$', '.nc', netcdf_filename)  # remove creation date

        # looking for product_name
        m = re.search('^IMOS_SRS-OC-LJCO_.*_([0-9]{8}T[0-9]{6}Z)_(SRC|LJCO)_FV0([0-2]{1}).*\.nc$', netcdf_filename)

        if m is None:
            raise InvalidFileNameError("file name not matching regex to deduce dest_path")

        # list of allowed products keywords
        products_type_ls = ['ACS', 'EcoTriplet', 'BB9', 'HyperOCR', 'WQM', 'DALEC']
        products_type = re.compile('|'.join(products_type_ls))
        nc_product_type = products_type.findall(netcdf_filename)

        # list of allowed time coverage keywords
        products_time_cov_ls = ['hourly', 'daily', 'monthly']
        products_time_cov = re.compile('|'.join(products_time_cov_ls))
        nc_product_time_cov = products_time_cov.findall(netcdf_filename)

        # netcdf qc value
        nc_product_qc = 'FV0%s' % m.group(3)

        nc_time_cov_start = datetime.strptime(m.group(1), '%Y%m%dT%H%M%SZ')
        nc_year = nc_time_cov_start.year
        nc_month = nc_time_cov_start.month
        nc_day = nc_time_cov_start.day

        if not nc_product_type:
            raise InvalidFileNameError(
                "can not find matching product type from allowed list: {product_type_ls}".format(
                    product_type_ls=products_type_ls))

        if nc_product_type[0] == 'DALEC':
            product_dir = nc_product_type[0]
        else:
            # products other than DALEC need to have product type AND time coverage info
            if len(nc_product_time_cov) == 0:
                raise InvalidFileNameError(
                    "can not find matching time coverage from allowed list: {products_time_cov_ls}".format(
                        products_time_cov_ls=products_time_cov_ls))
            else:
                product_dir = '%s-%s' % (nc_product_type[0], nc_product_time_cov[0])

        nc_common_dir_structure_prefix = os.path.join(ljco_s3_base_dir, product_dir, '%d' % nc_year)

        # DALEC doesn't have nc_product_time_cov keywords, so we run this section first
        if nc_product_type[0] == 'DALEC':
            if nc_product_qc == 'FV02':
                return os.path.join(nc_common_dir_structure_prefix,
                                    '%02d' % nc_month, 'fv02-products', netcdf_filename)
            else:
                return os.path.join(nc_common_dir_structure_prefix,
                                    '%02d' % nc_month, netcdf_filename)

        if nc_product_time_cov[0] == 'hourly':
            return os.path.join(nc_common_dir_structure_prefix,
                                '%02d' % nc_month, '%02d' % nc_day, netcdf_filename)

        if nc_product_time_cov[0] == 'daily':
            return os.path.join(nc_common_dir_structure_prefix, netcdf_filename)
