#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Burst Average Product creation from WQM and CTD FV01 files
./burst_average_product.py input_netcdf.nc /output_dir
"""


import argparse
import os
import re
import shutil
import sys
import tempfile
import time

from collections import OrderedDict
from datetime import datetime
from math import isnan
from pkg_resources import resource_filename

import numpy as np
import pandas as pd
from netCDF4 import Dataset, date2num, num2date

from aodntools.ncwriter import ImosTemplate
from aodndata.moorings.classifiers import MooringsFileClassifier
from aodndata.version import __version__


TEMPLATE_JSON = resource_filename('aodndata', 'templates/moorings_burst_average_template.json')


def get_input_file_rel_path(input_netcdf_file_path):
    """
    find the relative path hierarchy of an input FV01 file. The value will be
    used in a gatt of the burst netcdf file
    """
    return MooringsFileClassifier.dest_path(input_netcdf_file_path)


def create_burst_average_var(netcdf_file_obj):
    """
    create burst data from all vars available in netcdf
    """
    time_values = get_time_val(netcdf_file_obj)
    varname_to_burst_average = list_var_to_average(netcdf_file_obj)
    burst_vars = {}

    for varname in varname_to_burst_average:
        var_values, var_qc_flag_exclusion = get_var_val_var_qc_exclusion(
            netcdf_file_obj, varname)

        burst_vars[varname] = burst_average_data(time_values, var_values, var_qc_flag_exclusion)

    return trim_timestamps_burst_vars(burst_vars)


def trim_timestamps_burst_vars(burst_vars):
    """
    Trip timestamps at the start and end of a FV02 file when all FV02 variables
    have a NaN value.
    In details, for every burst var created, look for the first index of non NaN
    value. The lower value will be the one kept, and the new start index of each
    burst variable including the TIME.
    """
    min_index = None
    for var in burst_vars.keys():
        var_mean_burst = burst_vars[var]['var_mean']  # first non TIME product
        if not np.isnan(var_mean_burst).all():
            min_index_var = next(x for x, y in enumerate(var_mean_burst) if not isnan(y))
        else:
            min_index_var = 0

        if min_index is None:
            min_index = min_index_var
        else:
            min_index = min(min_index, min_index_var)

    # remove the first common NaN to all variables
    for var in burst_vars.keys():
        for product in burst_vars[var].keys():
            burst_vars[var][product] = burst_vars[var][product][min_index:-1]

    # look for last non NaN. we just have to reverse the list
    max_non_nan_idx = None
    for var in burst_vars.keys():
        var_mean_burst = burst_vars[var]['var_mean']  # first non TIME product
        var_mean_burst = pd.Series(var_mean_burst)  # create a pandas series to find easily last non nan index
        max_last_non_nan_var = var_mean_burst.last_valid_index()
        if max_non_nan_idx is None:
            max_non_nan_idx = max_last_non_nan_var
        else:
            max_non_nan_idx = max(max_non_nan_idx, max_last_non_nan_var)

    # remove the last common NaN to all variables
    if max_non_nan_idx is not None:
        for var in burst_vars.keys():
            for product in burst_vars[var].keys():
                burst_vars[var][product] = burst_vars[var][product][:max_non_nan_idx]

    return burst_vars


def get_time_val(netcdf_file_obj):
    """
    return the TIME numeric values from a NetCDF file
    """
    return netcdf_file_obj.variables['TIME'][:]


def get_var_val_var_qc_exclusion(netcdf_file_obj, varname):
    """
    for a qc flag values [0:9], returns the var_values array, and var_qc_flag_exclusion
    which is a boolean array returning True for all qc >= qc_flag

    Also exlude all TIME values outside of deployment range as defined in gatts
    """
    min_imos_qc_flag_val_exluded = 3
    var_values = netcdf_file_obj.variables[varname][:]
    var_qc_flag_exclusion = netcdf_file_obj.variables['%s_quality_control' % varname][:] >= min_imos_qc_flag_val_exluded

    # we exclude as well ALL TIMES before date_deployment_start, and after
    # date_deployment_end
    time = netcdf_file_obj.variables['TIME']
    date_deployment_start = date2num(datetime.strptime(netcdf_file_obj.time_deployment_start, '%Y-%m-%dT%H:%M:%SZ'),
                                     time.units, time.calendar)
    date_deployment_end = date2num(datetime.strptime(netcdf_file_obj.time_deployment_end, '%Y-%m-%dT%H:%M:%SZ'),
                                   time.units, time.calendar)

    time_before = date_deployment_start >= time[:]
    time_after = date_deployment_end <= time[:]

    var_qc_flag_exclusion = [a or b for a, b in zip(time_before, var_qc_flag_exclusion)]
    var_qc_flag_exclusion = [a or b for a, b in zip(time_after, var_qc_flag_exclusion)]

    return var_values, var_qc_flag_exclusion


def list_var_to_average(netcdf_file_obj):
    """
    return a list of variable to create a burst average for
    """
    var_list = netcdf_file_obj.variables.keys()
    var_list = [x for x in var_list if not x.endswith('_quality_control')]

    var_to_remove = []
    for varname in var_list:
        if 'TIME' not in netcdf_file_obj.variables[varname].dimensions:
            var_to_remove.append(varname)

    var_to_remove.extend(('TIME', 'VOLT', 'SSPD', 'CNDC', 'SPEC_CNDC'))
    var_list = [x for x in var_list if x not in var_to_remove]

    return var_list


def list_dimensionless_var(netcdf_file_obj):
    var_list = netcdf_file_obj.variables.keys()
    dimless_var = []
    for varname in var_list:
        if len(netcdf_file_obj.variables[varname].dimensions) == 0:
            dimless_var.append(varname)
    return dimless_var


def burst_average_data(time_values, var_values, var_qc_exclusion):
    """
    create burst average data for var_values. This is the core of the script
    """
    n_seconds_day = 24 * 3600
    difft = np.round(np.diff(time_values) * n_seconds_day)  # this gives us a spike for each new burst
    fill_value = float('nan')

    # look for start index of each burst, ie the index of each new spike of
    # difft variable
    idx_spike = [0]  # initialise first index
    spikes = np.where(difft > INSTRUMENT_SAMPLE_INTERVAL)[0] + 1
    idx_spike.extend(spikes)
    if idx_spike == [0]:
        raise Exception('No burst was found in time values - FV01 is probably already averaged')

    # initialise arrays
    time_mean_burst = []
    var_mean_burst = []
    var_min_burst = []
    var_max_burst = []
    var_sd_burst = []
    var_num_obs_burst = []

    for idx_spike_idx, idx_spike_val in enumerate(idx_spike[:-1]):
        index_burst_range = range(idx_spike_val, idx_spike[idx_spike_idx + 1])

        # burst average of TIME variable. All the range of the burst is used
        time_mean_burst.append((time_values[index_burst_range[0]] + time_values[index_burst_range[-1]]) / 2)

        # For NON TIME variables, the operations are only performed in respect
        # to boolean values found in var_qc_exclusion variable.
        # this var_qc_exclusion variable is set to True for all IMOS IODE flags
        # greater than a specific value
        valid_index_burst_range = [val for val in index_burst_range if not var_qc_exclusion[val]]

        # condition in case no good qc data was found for one burst
        if valid_index_burst_range:
            var_mean_burst.append(np.mean(var_values[valid_index_burst_range]))
            var_min_burst.append(np.min(var_values[valid_index_burst_range]))
            var_max_burst.append(np.max(var_values[valid_index_burst_range]))
            var_sd_burst.append(np.std(var_values[valid_index_burst_range]))
            var_num_obs_burst.append(len(valid_index_burst_range))
        else:
            var_mean_burst.append(fill_value)
            var_min_burst.append(fill_value)
            var_max_burst.append(fill_value)
            var_sd_burst.append(fill_value)
            var_num_obs_burst.append(0)

    burst_var = {'time_mean': time_mean_burst,
                 'var_mean': var_mean_burst,
                 'var_min': var_min_burst,
                 'var_max': var_max_burst,
                 'var_sd': var_sd_burst,
                 'var_num_obs': var_num_obs_burst}

    return burst_var


def generate_netcdf_burst_filename(input_netcdf_file_path, template):
    """
    Generate the filename of a burst average netcdf for both CTD and WQM. Template should already have
    the time variable fully defined (calendar, units, data values).
    """
    input_netcdf_name = os.path.basename(input_netcdf_file_path)
    pattern = re.compile("^(IMOS_.*)_([0-9]{8}T[0-9]{6}Z)_(.*)_(FV0[0-9])_(.*)_END")
    match_group = pattern.match(input_netcdf_name)

    site_code = template.global_attributes['site_code']

    time_range = template.get_data_range('TIME')
    time = template.variables['TIME']
    time_range = num2date(time_range, time.get('units'), time.get('calendar', 'gregorian'))
    timestamp_format = '%Y%m%dT%H%M%SZ'
    time_min = time_range[0].strftime(timestamp_format)
    time_max = time_range[1].strftime(timestamp_format)
    time_created = template.date_created.strftime(timestamp_format)

    burst_filename = "%s_%s_%s_FV02_%s-burst-averaged_END-%s_C-%s.nc" % (match_group.group(1), time_min,
                                                                         site_code, match_group.group(5),
                                                                         time_max, time_created)
    return burst_filename


def create_burst_average_netcdf(input_netcdf_file_path, output_dir):
    """
    generate the burst netcdf file for WQM product.
    see variable conf_file if editing of gatt and var att need to be done
    """
    input_file_rel_path = get_input_file_rel_path(input_netcdf_file_path)
    input_netcdf_obj = Dataset(input_netcdf_file_path, 'r')

    global INSTRUMENT_SAMPLE_INTERVAL
    INSTRUMENT_SAMPLE_INTERVAL = getattr(input_netcdf_obj, 'instrument_sample_interval', 1)

    burst_vars = create_burst_average_var(input_netcdf_obj)
    time_burst_vals = burst_vars.values()[0]['time_mean']
    tmp_netcdf_dir = tempfile.mkdtemp()

    template = ImosTemplate.from_json(TEMPLATE_JSON)

    # read gatts from input, add them to output. Some gatts will be overwritten
    gatt_to_dispose = ['author', 'author_email', 'file_version', 'file_version_quality_control', 'quality_control_set',
                       'compliance_checker_version', 'compliance_checker_last_updated',
                       'quality_control_log']
    update_gatts = {k: v
                    for k, v in input_netcdf_obj.__dict__.items()
                    if k not in gatt_to_dispose
                    }
    template.global_attributes.update(update_gatts)

    # create title attribute
    product = ''
    if 'WQM' in input_netcdf_obj.instrument:
        product = 'biogeochemical'
    elif 'CTD' in input_netcdf_obj.instrument:
        product = 'moored CTD'
    template.global_attributes['title'] = 'Burst-averaged {product} measurements at {site_code}'.format(
        product=product, site_code=input_netcdf_obj.site_code
    )

    template.global_attributes['input_file'] = input_file_rel_path
    template.add_date_created_attribute()

    # set up variables

    dimensionless_var = list_dimensionless_var(input_netcdf_obj)
    # No FillValue for dimensions as for IMOS conventions
    for var in dimensionless_var:
        template.variables[var] = {
            '_datatype': input_netcdf_obj[var].dtype,
            '_data': input_netcdf_obj[var][:]
        }

    for var in burst_vars.keys():
        input_var_object = input_netcdf_obj[var]
        var_dtype = input_var_object.dtype
        fillvalue = getattr(input_var_object, '_FillValue', None)

        var_att_template = OrderedDict({'_dimensions': ['TIME'],
                                        '_datatype': var_dtype,
                                        '_FillValue': fillvalue})

        for outvar in (var, var+'_burst_min', var+'_burst_max', var+'_burst_sd'):
            template.variables[outvar] = var_att_template.copy()
        template.variables[var+'_num_obs'] = OrderedDict({'_dimensions': ['TIME'],
                                                          '_datatype': 'int16'
                                                          })

        output_var_mean = template.variables[var]
        output_var_min = template.variables[var+'_burst_min']
        output_var_max = template.variables[var+'_burst_max']
        output_var_sd = template.variables[var+'_burst_sd']
        output_var_num_obs = template.variables[var+'_num_obs']

        # set up 'bonus' var att from original FV01 file into FV02
        var_att_disposable = ['name', 'long_name',
                              '_FillValue', 'ancillary_variables',
                              'ChunkSize', 'coordinates']
        update_atts = input_var_object.__dict__.copy()
        for att in var_att_disposable:
            update_atts.pop(att, None)

        output_var_mean.update(update_atts)
        update_atts.pop('comment', None)
        output_var_min.update(update_atts)
        output_var_max.update(update_atts)
        output_var_sd.update(update_atts)

        # make sur standard_deviation variable doesnt have a standard_name attr
        output_var_sd.pop('standard_name', None)

        output_var_mean.update([
            ('coordinates', getattr(input_var_object, 'coordinates', '')),
            ('ancillary_variables', ('{var}_num_obs {var}_burst_sd {var}_burst_min {var}_burst_max'.format(var=var)))
        ])

        output_var_mean['cell_methods'] = 'TIME: mean'
        output_var_min['cell_methods'] = 'TIME: minimum'
        output_var_max['cell_methods'] = 'TIME: maximum'
        output_var_sd['cell_methods'] = 'TIME: standard_deviation'

        output_var_sd['long_name'] = 'Standard deviation of values in burst, after rejection of flagged data'
        output_var_num_obs['long_name'] = 'Number of observations included in the averaging process'
        output_var_min['long_name'] = 'Minimum data value in burst, after rejection of flagged data'
        output_var_max['long_name'] = 'Maximum data value in burst, after rejection of flagged data'
        output_var_mean['long_name'] = 'Mean of %s values in burst, after rejection of flagged data' % (
            getattr(input_var_object, 'standard_name', getattr(input_var_object, 'long_name', '')))

        output_var_num_obs['units'] = "1"
        var_units = getattr(input_var_object, 'units')
        if var_units:
            output_var_mean['units'] = var_units
            output_var_min['units'] = var_units
            output_var_max['units'] = var_units
            output_var_sd['units'] = var_units

        var_stdname = getattr(input_var_object, 'standard_name', '')
        if var_stdname != '':
            output_var_num_obs['standard_name'] = "%s number_of_observations" % var_stdname

        # set up var values
        output_var_mean['_data'] = np.ma.masked_invalid(burst_vars[var]['var_mean'])
        output_var_min['_data'] = np.ma.masked_invalid(burst_vars[var]['var_min'])
        output_var_max['_data'] = np.ma.masked_invalid(burst_vars[var]['var_max'])
        output_var_sd['_data'] = np.ma.masked_invalid(burst_vars[var]['var_sd'])
        output_var_num_obs['_data'] = np.ma.masked_invalid(burst_vars[var]['var_num_obs'])

    # set up original varatts for the following dim, var
    varnames = dimensionless_var
    varnames.append('TIME')
    for var in varnames:
        template.variables[var].update(input_netcdf_obj[var].__dict__)

    time_comment = '%s. Time stamp corresponds to the middle of the burst measurement.' % getattr(
        input_netcdf_obj['TIME'], 'comment', '')
    template.variables['TIME']['comment'] = time_comment.lstrip('. ')

    # append original gatt to burst average gatt
    if hasattr(input_netcdf_obj, 'comment'):
        template.global_attributes['comment'] = input_netcdf_obj.comment

    gatt = 'history'
    template.global_attributes[gatt] = '{old}. Created {new}'.format(old=getattr(input_netcdf_obj, gatt, ''),
                                                                     new=time.ctime(time.time())
                                                                     ).lstrip('. ')

    gatt = 'abstract'
    template.global_attributes[gatt] = '{old}. {new}'.format(old=getattr(input_netcdf_obj, gatt, ''),
                                                             new='Data from the bursts have been cleaned and averaged '
                                                                 'to create this product.'
                                                             ).lstrip('. ')

    # add burst keywords
    gatt = 'keywords'
    keywords_burst = 'AVERAGED, BINNED'
    template.global_attributes[gatt] = '{old}, {new}'.format(old=getattr(input_netcdf_obj, gatt, ''),
                                                             new=keywords_burst
                                                             ).lstrip(', ')

    # add values to variables
    template.variables['TIME']['_data'] = np.ma.masked_invalid(time_burst_vals)

    github_comment = (' Product created with https://github.com/aodn/python-aodndata'
                      '/blob/{v}/aodndata/moorings/burst_average.py'.format(v=__version__)
                      )
    template.global_attributes['lineage'] += github_comment

    try:
        template.add_extent_attributes(lat_var=None, lon_var=None)
    except ValueError:
        template.add_extent_attributes(vert_var='NOMINAL_DEPTH', lat_var=None, lon_var=None)

    template.to_netcdf(os.path.join(tmp_netcdf_dir, generate_netcdf_burst_filename(input_netcdf_file_path, template)))
    input_netcdf_obj.close()

    shutil.move(template.outfile, output_dir)
    shutil.rmtree(tmp_netcdf_dir)
    return os.path.join(output_dir, os.path.basename(template.outfile))


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_fv01_netcdf_path", type=str, help="path to CTD or WQM FV01 netcdf file")
    parser.add_argument("output_dir", type=str, help="output directory of FV02 netcdf file")
    vargs = parser.parse_args()

    if not os.path.exists(vargs.input_fv01_netcdf_path):
        msg = '%s not a valid path' % vargs.input_netcdf_file_path
        print >> sys.stderr, msg
        sys.exit(1)
    elif not os.path.exists(vargs.output_dir):
        msg = '%s not a valid path' % vargs.output_dir
        print >> sys.stderr, msg
        sys.exit(1)

    return vargs


if __name__ == "__main__":
    vargs = args()
    burst_file_path = create_burst_average_netcdf(vargs.input_fv01_netcdf_path, vargs.output_dir)
    print burst_file_path
