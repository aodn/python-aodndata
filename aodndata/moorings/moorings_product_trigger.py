#! /usr/bin/env python3

import argparse
import json
import logging
import os

from shutil import copyfile
from tempfile import NamedTemporaryFile
from typing import Union

import numpy as np
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, And, Or

import pandas as pd

# Variables included in the products
INCLUDED_VARIABLES = {'TEMP', 'PSAL', 'CPHL', 'CHLF', 'CHLU', 'TURB', 'DOX1', 'DOX2', 'DOXS', 'PAR', 'VCUR'}

# Geoserver details
WFS_URL = "http://geoserver-123.aodn.org.au/geoserver/wfs"
WFS_VERSION = '1.1.0'
WFS = None
FILE_INDEX_LAYER = 'imos:moorings_all_map'


def get_wfs_service(url: str = WFS_URL, version: str = WFS_VERSION) -> WebFeatureService:
    """connect to WFS server"""
    wfs = WebFeatureService(url, version=version)
    logging.debug(f"Connected to {url}")

    return wfs


def get_files_dataframe(filters: list = None,
                        propertyname: Union[str, list] = '*',
                        getfeature_kwargs: dict = None,
                        read_csv_kwargs: dict = None
                        ) -> pd.DataFrame:
    """Query the file index WFS layer with the given filters and return a DataFrame

    :param filters: list of filters to apply (owslib.fes.OgcExpression instances)
    :param propertyname: str or list of property name(s) to return (default all)
    :param getfeature_kwargs: additional arguments for WFS getfeature
    :param read_csv_kwargs: additional arguments for pandas.read_csv
    :return: DataFrame of file details
    """
    global WFS
    if not WFS:
        WFS = get_wfs_service()

    gf_kwargs = getfeature_kwargs.copy() if getfeature_kwargs else {}
    gf_kwargs.update(propertyname=propertyname, outputFormat='csv')
    if filters:
        gf_kwargs['filter'] = etree.tostring(And(filters).toXML(), encoding='unicode')

    with WFS.getfeature(typename=FILE_INDEX_LAYER, **gf_kwargs) as response:
        df = pd.read_csv(response, **read_csv_kwargs)

    # drop useless FID column
    df.drop(columns='FID', inplace=True)
    return df


def files_for_site(site_code: str) -> pd.DataFrame:
    """Query geoserver-123 to get a DataFrame of currently availabe FV01 source files for the given site_code"""

    logging.debug(f"Getting file list for site {site_code}...")

    filter_list = [PropertyIsEqualTo(propertyname='site_code', literal=site_code),
                   Or([PropertyIsEqualTo(propertyname='file_version', literal='1'),
                       PropertyIsEqualTo(propertyname='file_version', literal='2')
                       ]),
                   PropertyIsEqualTo(propertyname='realtime', literal='false'),
                   PropertyIsNotEqualTo(propertyname='data_category', literal='Biogeochem_profiles'),
                   PropertyIsNotEqualTo(propertyname='data_category', literal='CTD_profiles'),
                   ]
    wfs_features = get_files_dataframe(filter_list,
                                       propertyname=['url', 'variables', 'date_created', 'date_updated',
                                                     'data_category', 'file_version'
                                                     ],
                                       read_csv_kwargs={'parse_dates': ['date_created', 'date_updated']}
                                       )
    logging.debug(f"  Returned {len(wfs_features)} features")

    return wfs_features


def pivot_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Rearrange the file-list data frame so that each row lists one variable only
     (multiple rows per file where needed)
    """
    assert 'variables' in df.columns
    files_vars = []
    for row in df.itertuples():
          variables = set(row.variables.split(', ')) & INCLUDED_VARIABLES
          files_vars.extend((row.Index, v) for v in variables)

    files_vars = pd.DataFrame(files_vars, columns=['i', 'variable']).set_index('i')

    return df.drop(columns='variables').join(files_vars)


def make_manifest(site_code: str) -> dict:
    """Create a manifest to trigger products creation for the given site"""

    files_df = files_for_site(site_code)

    source_index = np.logical_and(files_df.file_version == 1,
                                  files_df.data_category.map(lambda s: s not in ('aggregated_timeseries', 'CO2'))
                                  )
    source_files = files_df.loc[source_index, ['url', 'date_updated', 'variables']]
    logging.info(f"Found {len(source_files)} source files, last updated {source_files.date_updated.max()}")
    source_files = pivot_variables(source_files)

    # product_files
    aggregated_files = files_df.loc[
        files_df.data_category == 'aggregated_timeseries', ['url', 'date_created', 'variables']]
    logging.info(f"Found {len(aggregated_files)} aggregated_timeseries files, "
                 f"last created {aggregated_files.date_created.max()}")
    aggregated_files = pivot_variables(aggregated_files)

    hourly_files = files_df.loc[files_df.data_category == 'hourly_timeseries', ['url', 'date_created']]
    logging.info(f"Found {len(hourly_files)} hourly_timeseries files, "
                 f"last created {hourly_files.date_created.max()}")

    # when were data for each variable updated?
    vars_updated = source_files.groupby('variable').date_updated.max()
    vars_updated.name = 'source_updated'
    aggregated_files = aggregated_files.join(vars_updated, on='variable', how='right')

    # which variables have newer data than the product, or missing product?
    new_vars = aggregated_files[np.logical_or(aggregated_files.date_created < aggregated_files.source_updated,
                                              aggregated_files.url.isna()
                                              )]
    new_vars = set(new_vars.variable)

    # reprocess hourly products if newer source files exist, or product files missing?
    products_updated = hourly_files.date_created.max()
    process_hourly = any(source_files.date_updated > products_updated) or hourly_files.empty

    if len(new_vars) == 0 and not process_hourly:
        logging.info(f"No new data for site {site_code}")
        return None

    # products to generate
    # VCUR is used as a proxy for all velocity variables - if included, need to handle separately
    products = set()
    if 'VCUR' in new_vars:
        new_vars.remove('VCUR')
        products.update({'velocity_aggregated', 'velocity_hourly'})
    if new_vars:
        products.add('aggregated')
    if process_hourly:
        # gridded is created from hourly, so need to process both
        products.update({'hourly', 'gridded'})

    # create manifest
    manifest = {'site_code': site_code,
                'variables': list(new_vars),
                'products': list(products)
                }
    return manifest


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("site_code", nargs="+", type=str, help="site_code(s) to process")
    parser.add_argument("-d", action="store_const", dest="loglevel", const=logging.DEBUG,
                        help="Log debugging output")
    parser.add_argument("-i", action="store_const", dest="loglevel", const=logging.INFO,
                        help="Log INFO output")
    parser.add_argument("-t", "--target_dir", default="/tmp",
                        help="target directory to push manifests to (default /tmp)")
    args = parser.parse_args()

    if hasattr(args, 'loglevel'):
        logging.basicConfig(level=args.loglevel)

    return args


if __name__ == "__main__":
    args = parse_args()

    for site_code in args.site_code:
        manifest = make_manifest(site_code)
        if manifest is not None:
            logging.info(manifest)
            with NamedTemporaryFile(mode="w") as f:
                json.dump(manifest, f, indent=4)
                f.flush()
                target_path = os.path.join(args.target_dir, f"{site_code}.json_manifest")
                copyfile(f.name, target_path)

    exit(0)