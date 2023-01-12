#! /bin/env python3
from typing import Union

import numpy as np
from owslib.etree import etree
from owslib.wfs import WebFeatureService
from owslib.fes import PropertyIsEqualTo, PropertyIsNotEqualTo, And, Or

import pandas as pd


WFS_URL = "http://geoserver-123.aodn.org.au/geoserver/wfs"
WFS_VERSION = '1.1.0'

FILE_INDEX_LAYER = 'imos:moorings_all_map'

# connect to WFS server
WFS = WebFeatureService(WFS_URL, version=WFS_VERSION)


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

    with WFS.getfeature(typename=FILE_INDEX_LAYER, **gf_kwargs) as response:
        df = pd.read_csv(response, **read_csv_kwargs)

    # drop useless FID column~
    df.drop(columns='FID', inplace=True)
    return df


def files_for_site(site_code: str) -> pd.DataFrame:
    """Query geoserver-123 to get a DataFrame of currently availabe FV01 source files for the given site_code"""

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
    
    return wfs_features

# Get all relevant FV01 & FV02 files for site
files_df = files_for_site('NRSMAI')


# source files
source_index = np.logical_and(files_df.file_version == 1,
                              files_df.data_category.map(lambda s: s not in ('aggregated_timeseries', 'CO2'))
                              )
source_files = files_df.loc[source_index, ['url', 'date_updated', 'variables']]

# product_files
aggregated_files = files_df.loc[files_df.data_category=='aggregated_timeseries', ['url', 'date_created']]
hourly_files = files_df.loc[files_df.data_category=='hourly_timeseries', ['url', 'date_created']]
gridded_files = files_df.loc[files_df.data_category=='gridded_timeseries', ['url', 'date_created']]
