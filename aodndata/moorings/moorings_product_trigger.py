#! /bin/env python3

import logging
from typing import Union

import numpy as np
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, And, Or

import pandas as pd

logging.basicConfig(level=logging.INFO)

# Variables included in the products
INCLUDED_VARIABLES = {'TEMP', 'PSAL', 'CPHL', 'CHLF', 'CHLU', 'TURB', 'DOX1', 'DOX2', 'DOXS', 'PAR', 'VCUR'}

# Geoserver details
WFS_URL = "http://geoserver-123.aodn.org.au/geoserver/wfs"
WFS_VERSION = '1.1.0'
FILE_INDEX_LAYER = 'imos:moorings_all_map'

# connect to WFS server
WFS = WebFeatureService(WFS_URL, version=WFS_VERSION)
logging.debug(f"Connected to {WFS_URL}")


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

    gf_kwargs = getfeature_kwargs.copy() if getfeature_kwargs else {}
    gf_kwargs.update(propertyname=propertyname, outputFormat='csv')
    if filters:
        gf_kwargs['filter'] = etree.tostring(And(filters).toXML(), encoding='unicode')

    logging.debug("  Sending query to geoserver")
    with WFS.getfeature(typename=FILE_INDEX_LAYER, **gf_kwargs) as response:
        df = pd.read_csv(response, **read_csv_kwargs)

    # drop useless FID column
    df.drop(columns='FID', inplace=True)
    return df


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


def files_for_site(site_code: str) -> pd.DataFrame:
    """Query geoserver-123 to get a DataFrame of currently availabe FV01 source files for the given site_code"""

    logging.info(f"Getting file list for site {site_code}...")

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
    logging.info(f"  Returned {len(wfs_features)} features")

    return pivot_variables(wfs_features)


# Get all relevant FV01 & FV02 files for site
site_code = 'GBRLSH'
files_df = files_for_site(site_code)

# source files
source_index = np.logical_and(files_df.file_version == 1,
                              files_df.data_category.map(lambda s: s not in ('aggregated_timeseries', 'CO2'))
                              )
source_files = files_df.loc[source_index, ['url', 'date_updated', 'variable']]
logging.info(f"Found {len(source_files.url.unique())} source files")

# product_files
aggregated_files = files_df.loc[files_df.data_category=='aggregated_timeseries', ['url', 'date_created', 'variable']]
hourly_files = files_df.loc[files_df.data_category=='hourly_timeseries', ['url', 'date_created']]

# when were data for each variable updated?
vars_updated = source_files.groupby('variable').date_updated.max()
vars_updated.name = 'source_updated'
aggregated_files = aggregated_files.join(vars_updated, on='variable', how='right')

# which variables have newer data than the product, or missing product
new_vars = aggregated_files[np.logical_or(aggregated_files.date_created < aggregated_files.source_updated,
                                          aggregated_files.url.isna()
                                          )]
new_vars = set(new_vars.variable)

# what source files have changed since the hourly products were last created?
products_updated = hourly_files.date_created.max()
new_source_hourly = source_files[source_files.date_updated > products_updated]

if len(new_vars) == 0 and new_source_hourly.empty:
    logging.info(f"No new data for site {site_code}")
    exit(0)

# products to generate
# VCUR is used as a proxy for all velocity variables - if included, need to handle separately
products = set()
if 'VCUR' in new_vars:
    new_vars.remove('VCUR')
    products.update({'velocity_aggregated', 'velocity_hourly'})
if new_vars:
    products.add('aggregated')
if not new_source_hourly.empty:
    products.update({'hourly', 'gridded'})

# create manifest
manifest = {'site_code': site_code,
            'variables': list(new_vars),
            'products': list(products)
            }
print(manifest)
