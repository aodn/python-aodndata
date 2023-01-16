#! /bin/env python3

import logging
from typing import Union

import numpy as np
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, And, Or

import pandas as pd

logging.basicConfig(level=logging.DEBUG)

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
              for v in variables:
                  files_vars.append((row.url, v))

    files_vars = pd.DataFrame(files_vars, columns=['url', 'variable']).set_index('url')

    return df.drop(columns='variables').join(files_vars, on='url')


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
site_code = 'NRSMAI'
files_df = files_for_site(site_code)

# source files
source_index = np.logical_and(files_df.file_version == 1,
                              files_df.data_category.map(lambda s: s not in ('aggregated_timeseries', 'CO2'))
                              )
source_files = files_df.loc[source_index, ['url', 'date_updated', 'variable']].set_index('url')
logging.info(f"Found {len(source_files)} source files")

# product_files
aggregated_files = files_df.loc[files_df.data_category=='aggregated_timeseries', ['url', 'date_created']]
logging.debug(f"Found {len(aggregated_files)} aggregated products")
hourly_files = files_df.loc[files_df.data_category=='hourly_timeseries', ['url', 'date_created']]
logging.debug(f"Found {len(hourly_files)} hourly products")

# when were any of the products last updated? - assume they were all up to date at that time
products_updated = max(aggregated_files.date_created.max(), hourly_files.date_created.max())
logging.info(f"Products last updated {products_updated}")

# what source files have changed since then and what variables were included?
new_source_files = source_files[source_files.date_updated > products_updated]
new_vars = set(new_source_files.variable)

if len(new_vars) == 0:
    logging.info(f"No new data for site {site_code}")
    exit(0)

# products to generate
# VCUR is used as a proxy for all velocity variables - if included, need to handle separately
products = set()
if 'VCUR' in new_vars:
    new_vars.remove('VCUR')
    products.update({'velocity_aggregated', 'velocity_hourly'})
if new_vars:
    products.update({'aggregated', 'hourly', 'gridded'})

# create manifest
manifest = {'site_code': site_code,
            'variables': list(new_vars),
            'products': list(products)
            }
print(manifest)
