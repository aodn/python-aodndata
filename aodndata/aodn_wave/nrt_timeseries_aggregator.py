#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import xarray as xr
from netCDF4 import Dataset, num2date, stringtochar
from pkg_resources import resource_filename

from aodntools.ncwriter import ImosTemplate
from aodntools.timeseries_products.common import (current_utc_timestamp)

TEMPLATE_JSON = resource_filename('aodndata', 'templates/aodn_wave_nrt_timeseries_template.json')


## MAIN FUNCTION
def file_aggregator(file_to_agg, src_file_path, products_dir, filename_fields):
    """
    Aggregate hourly file into monthly timeseries file.
    Find the monthly timeseries file to aggreagte with and create the aggregated netcdf file
    :param: file_to_agg file to aggregate to monthy product (pipelinefile)
    :param: src_file_path  path or name of existing aggregated file
    :param: products_dir directory where the product is created
    :param: filename_fields fields making up the filename (list)
    :return:  aggregated file path
    """

    to_agg_df, to_agg_nc = extract_variable(file_to_agg.src_path)

    if src_file_path:
        # extract variables from files and aggregate into a dataframe
        aggregated_filename = os.path.basename(src_file_path)
        aggregated_file_path = os.path.join(products_dir, aggregated_filename)
        source_df, source_nc = extract_variable(src_file_path)
    else:
        aggregated_filename = make_monthly_product_name(filename_fields)
        aggregated_file_path = os.path.join(products_dir, aggregated_filename)
        source_df = pd.DataFrame()
        source_nc = to_agg_nc

    # aggregate dataframes
    source_df = source_df.append(to_agg_df, ignore_index=True)

    # dataframe to store template of new aggregated file
    template = ImosTemplate.from_json(TEMPLATE_JSON)
    # add attributes to template
    set_template_attributes(template, to_agg_nc, source_nc, source_df)

    for var in list(source_df.keys()):
        template.variables[var]['_data'] = source_df[var].values

    template.variables['timeSeries']['_data'] = [1]
    # Remove empty varaibles from template
    template_vars = set(template.variables.keys())
    data_vars = set(source_df.keys())
    data_vars.add('timeSeries')
    excluded_vars = template_vars.difference(data_vars)
    for excl_var in excluded_vars:
        template.variables.pop(excl_var)

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
        varlist = set(nc.variables)
        #Time and timeSeries traeted separately
        varlist.remove('TIME')
        varlist.remove('timeSeries')

        TIME = pd.DataFrame((nc.TIME.values - epoch) / np.timedelta64(1, 'D'))  # convert to number of days since 1950
        TIME.columns = ['TIME']
        df = TIME

        for var in varlist:
            df = get_variable_values(nc, df ,var)

    return df, nc

def make_monthly_product_name(fields):
    """generate product filename
    params: fields list of string
    :return filename string
    """
    institution = fields['institution']
    nc_time_cov_start = fields['nc_time_cov_start']
    site_name = fields['site_name']
    mode = fields['mode']
    datatype = fields['datatype']
    filename = ('{institution}_{time_start}_{site_name}_{mode}_{datatype}_monthly.nc'.format(
        institution=institution,
        time_start=nc_time_cov_start,
        site_name=site_name,
        mode=mode,
        datatype=datatype
    ))
    return filename


def set_template_attributes(template, to_agg_nc,source_nc, source_df):
    """set attribute using json config. Update datatype when needed
     :params: template
     :params: to_agg_nc  incoming file (xarray dataset)
     :params: source_nc existing monthly file (xarray dataset)
     :params: source_df existing monthly data (dataframe)
     :returns: updated template
     """
    template.global_attributes.update({'site_name': to_agg_nc.site_name,
                                       'institution': to_agg_nc.institution,
                                       'wave_buoy_type': to_agg_nc.wave_buoy_type,
                                       'instrument': to_agg_nc.instrument,
                                       'instrument_burst_interval': int(to_agg_nc.instrument_burst_interval),
                                       'instrument_burst_duration': int(to_agg_nc.instrument_burst_duration),
                                       'instrument_burst_units': to_agg_nc.instrument_burst_units,
                                       'instrument_sampling_interval': float(to_agg_nc.instrument_sampling_interval),
                                       'wave_motion_sensor_type': to_agg_nc.wave_motion_sensor_type,
                                       'wave_sensor_serial_number': to_agg_nc.wave_sensor_serial_number,
                                       'hull_serial_number': to_agg_nc.hull_serial_number,
                                       'transmission': to_agg_nc.transmission,
                                       'water_depth': int(to_agg_nc.water_depth),
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
    # add wmo_id where applicable
    if 'wmo_id' in to_agg_nc.attrs.keys():
        template.global_attributes.update({'wmo_id': to_agg_nc.wmo_id})

    # ensure WAVE qc attribute are of type byte
    template.variables['WAVE_quality_control']['flag_values'] = np.int8([1, 2, 3, 4, 9])
    template.variables['WAVE_quality_control']['valid_min'] = np.int8(1)
    template.variables['WAVE_quality_control']['valid_max'] = np.int8(9)

def get_variable_values(nc, df, variable):
    """
    Get values of the variable and append to DataFrame

    :param nc: xarray dataset
    :param variable: name of the variable to get
    :return: data dataframe
    """
    file_variables = list(nc.variables)
    if variable in file_variables:
        data = pd.DataFrame(nc[variable].values)
        data.columns = [variable]
        df = df.join(data)

    return df