#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import tempfile

import pandas as pd
import numpy as np
import xarray as xr
from netCDF4 import Dataset, num2date, stringtochar
from pkg_resources import resource_filename

from aodntools.ncwriter import ImosTemplate
from aodntools.timeseries_products.common import (NoInputFilesError, check_file, in_water, current_utc_timestamp,
                                                  TIMESTAMP_FORMAT, DATESTAMP_FORMAT)

TEMPLATE_JSON = resource_filename('aodndata', 'templates/aodn_wave_nrt_timeseries_template.json')

## MAIN FUNCTION
def file_aggregator(file_to_agg, src_file_path, products_dir, filename_fields):
    """
    Aggregate hourly file into monthly timeseries file.
    Find the monthly timeseries file to aggreagte with and create the aggregated netcdf file
    :param: file_to_agg file to aggregate to monthy product (pipelinefile)
    :param: src_file_path  path or name of existing aggregated file
    :param: filename_fields fields making up the filename (list)
    :return:  aggregated file path
    """

    institution = filename_fields['institution']
    nc_time_cov_start = filename_fields['nc_time_cov_start']
    site_name = filename_fields['site_name']
    mode = filename_fields['mode']
    datatype = filename_fields['datatype']
    aggregated_filename = ('{institution}_{time_start}_{site_name}_{mode}_{datatype}_monthly.nc'.format(
        institution=institution,
        time_start=nc_time_cov_start,
        site_name=site_name,
        mode=mode,
        datatype=datatype
    ))
    aggregated_file_path = os.path.join(products_dir, aggregated_filename) #new product name
    to_agg_df, to_agg_nc = extract_variable(file_to_agg.src_path)

    if src_file_path is not None:
        # extract variables from files and aggregate into a dataframe
        source_df, source_nc = extract_variable(os.path.join(src_file_path))
    else:
        source_df = pd.DataFrame()
        source_nc = to_agg_nc

    # aggregate dataframes
    source_df = source_df.append(to_agg_df, ignore_index=True)

    # dataframe to store template of new aggregated file
    template = ImosTemplate.from_json(TEMPLATE_JSON)
    # copy attribute to new file
    template.global_attributes.update({'site_name': to_agg_nc.site_name,
                                       'institution': to_agg_nc.institution,
                                       'wave_buoy_type': to_agg_nc.wave_buoy_type,
                                       'instrument': to_agg_nc.instrument,
                                       'instrument_burst_interval': to_agg_nc.instrument_burst_interval,
                                       'instrument_burst_duration': to_agg_nc.instrument_burst_duration,
                                       'instrument_burst_units': to_agg_nc.instrument_burst_units,
                                       'instrument_sampling_interval': to_agg_nc.instrument_sampling_interval,
                                       'wave_motion_sensor_type': to_agg_nc.wave_motion_sensor_type,
                                       'wave_sensor_serial_number': to_agg_nc.wave_sensor_serial_number,
                                       'hull_serial_number': to_agg_nc.hull_serial_number,
                                       'transmission': to_agg_nc.transmission,
                                       'water_depth': to_agg_nc.water_depth,
                                       'water_depth_units': to_agg_nc.water_depth_units,
                                       'geospatial_lat_min': min(source_df['LATITUDE']),
                                       'geospatial_lat_max': max(source_df['LATITUDE']),
                                       'geospatial_lon_min': min(source_df['LONGITUDE']),
                                       'geospatial_lon_max': max(source_df['LONGITUDE']),
                                       'date_created': current_utc_timestamp(),
                                       'time_coverage_start': source_nc.time_coverage_start,
                                       'time_coverage_end': to_agg_nc.time_coverage_end,
                                       'title': ('Near real time wave buoy observations at {site} '
                                                 'from {start} to {end}').format(site=to_agg_nc.site_name,
                                                                                 start=source_nc.time_coverage_start,
                                                                                 end=to_agg_nc.time_coverage_end),
                                       'abstract': ('Near real time integral wave parameters from wave buoys'
                                                    ' collected by the {institution} using a {instrument} at '
                                                    '{site} between {start} and {end}. Data have been aggregated '
                                                    'into a monthly product').format(institution=to_agg_nc.institution,
                                                                                     instrument=to_agg_nc.instrument,
                                                                                     site=to_agg_nc.site_name,
                                                                                     start=source_nc.time_coverage_start,
                                                                                     end=to_agg_nc.time_coverage_end)})
    template.add_date_created_attribute()
    # ensure WAVE qc attribute are of type byte
    template.variables['WAVE_quality_control']['flag_values'] = np.int8([1, 2, 3, 4, 9])
    template.variables['WAVE_quality_control']['valid_min'] = np.int8(1)
    template.variables['WAVE_quality_control']['valid_max'] = np.int8(9)

    for var in list(source_df.keys()):
        template.variables[var]['_data'] = source_df[var].values

    template.variables['Timeseries']['_data'] = [1]
    #### verifier values for TIME
    ## create temporary aggregated file -  with filename identical to monthly source file
    template.to_netcdf(aggregated_file_path)

    return aggregated_file_path


def extract_variable(filepath):
    """extract variable from netcdf file
        :param filepath str path f source file
        :return df dataframe containing all variables in the file
        :return nc xarray of netcdf content
    """
    epoch = np.datetime64("1950-01-01T00:00:00")
    with xr.open_dataset(filepath) as nc:
        TIME = (nc.TIME.values - epoch) / np.timedelta64(1, 'D')  # convert to number of days since 1950
        LATITUDE = nc.LATITUDE.values
        LONGITUDE = nc.LONGITUDE.values
        WHTH = nc.WHTH.values
        WMXH = nc.WMXH.values
        WPPE = nc.WPPE.values
        WPMH = nc.WPMH.values
        WPDI = nc.WPDI.values
        WPDS = nc.WPDS.values
        WAVE_quality_control = np.int8(nc.WAVE_quality_control.values)

    df = pd.DataFrame({'TIME': TIME, 'LATITUDE': LATITUDE, 'LONGITUDE': LONGITUDE, 'WHTH': WHTH, 'WMXH': WMXH,
                       'WPPE': WPPE, 'WPMH': WPMH, 'WPDI': WPDI, 'WPDS': WPDS,
                       'WAVE_quality_control': WAVE_quality_control})
    nc.close()
    return df, nc
