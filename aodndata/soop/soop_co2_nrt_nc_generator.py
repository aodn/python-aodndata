"""
# generate NetCDF file storing realtime SOOP-CO2 data.
# Script processes data from 2 vessels: RV Aurora Australis and RV Investigator
# -Extract variable relevant to CO2 measurements and processing from input text file.
# -Map vessel specific variable to set of common output variables
# Mapping as follows:
#       Input Variable                  NetCDF Variable
#   Aurora      Investigator
#       PcDate+PcTime                        TIME
#       GpsShipLatitude                     LATITUDE
#       GpsShipLongitude                    LONGITUDE
#           Type                            TYPE
#           EquTemp                         TEQ_raw
#           CO2StdValue                     CO2_STD_Value
#           CO2um_m                         xCO2_PPM_raw
#           H2Omm_m                         xH2O_PPT_raw
#       DryBoxDruckPress                    Press_Licor_raw
#           EquPress                        Diff_Press_Equ_raw
#           EquH2OFlow                      H2O_flow_raw
#           LicorFlow                       Licor_flow_raw
#           AtmSeaLevelPress                ATMP_raw
#           MetTrueWindSpKts                WSPD_raw
#           MetTrueWindDir                  WDIR_raw
#           IntakeShipTemp                  TEMP_raw
# TsgSbe45Salinity  TsgShipSalinity          PSAL_raw
# TsgSbe45Temp      TsgShipTemp             TEMP_Tsg_raw
# SBE45Flow         TsgShipFlow             Tsg_flow_raw
#    -             LabMainSwFlow            LabMain_sw_flow_raw
"""

import collections
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from aodncore.pipeline.exceptions import InvalidFileContentError
from netCDF4 import Dataset, stringtochar

from .ship_callsign import ship_callsign_list, ship_callsign

VALID_PROJECT = ['IMOS', 'FutureReefMap', 'SOOP-CO2_RT']
INPUT_RT_PARAMETERS = {'Type', 'PcDate', 'PcTime', 'GpsShipLatitude',
                       'GpsShipLongitude', 'EquTemp', 'CO2StdValue',
                       'CO2um_m', 'H2Omm_m', 'DryBoxDruckPress', 'EquPress',
                       'EquH2OFlow', 'LicorFlow', 'IntakeShipTemp', 'MetTrueWindSpKts',
                       'MetTrueWindDir', 'AtmSeaLevelPress'}
AA_SPECIFIC_INPUT_PARAMS = {'SBE45Flow', 'TsgSbe45Temp',
                            'TsgSbe45Salinity'}
IN_SPECIFIC_INPUT_PARAMS = {'TsgShipTemp',
                            'TsgShipSalinity', 'TsgShipFlow', 'LabMainSwFlow'}

VESSEL = {
    'AA': 'VNAA',
    'IN': 'VLMJ'}


def process_co2_rt(realtime_file, temp_dir):
    """
    Read in data from co2 realtime file and produce a netcdf file
    """
    # Parse data into dataframe
    (dataf, platform_code) = read_realtime_file(realtime_file)
    # format data
    (dtime, time) = get_time_formatted(dataf)
    # generate nc file name
    netcdf_filename = create_netcdf_filename(platform_code, dtime)
    netcdf_file_path = os.path.join(temp_dir, "%s.nc") % netcdf_filename

    create_netcdf(netcdf_file_path, dataf, dtime, time, realtime_file.src_path, platform_code)

    return netcdf_file_path


def create_netcdf_filename(platform_code, dtime):
    """
    Generate filename
    """
    facility_param = 'IMOS_SOOP-CO2_GST'
    prodtype = 'FV00'
    time_start = min(dtime).strftime("%Y%m%dT%H%M%SZ")
    time_end = max(dtime).strftime("%Y%m%dT%H%M%SZ")
    filename = "%s_%s_%s_%s_END-%s" % (facility_param, time_start, platform_code, prodtype, time_end)

    return filename


def get_time_formatted(dataf):
    """
    Convert date and time data object into datetime
    Input : data Frame
    Return:
         - time:array of decimal time from 1950-01-01T00:00:00
         - dtime: array of datetime object
    """
    epoch = datetime(1950, 1, 1)
    time = []
    time_long = dataf['PcDate'].values + ' ' + dataf['PcTime'].values
    dtime = pd.to_datetime(time_long, dayfirst=True, utc=True)
    for t in dtime:
        dt = datetime.strptime(datetime.strftime(
            t, '%d/%m/%Y %H:%M:%S'), '%d/%m/%Y %H:%M:%S')
        time.append((dt - epoch).total_seconds())

    return dtime, np.array(time) / 3600. / 24.


def create_netcdf(netcdf_file_path, dataf, dtime, time, src_file, platform_code):
    """
    Create the netcdf file
    """
    ncfile = Dataset(netcdf_file_path, "w", format="NETCDF4")
    # TO ENABLE
    #  config_file = os.path.join(
    #     os.getenv('DATA_SERVICES_DIR'), 'SOOP', 'SOOP_CO2', 'global_att_soop_co2.att')

    if platform_code in ship_callsign_list():
        vessel_name = ship_callsign(platform_code)
    else:
        raise InvalidFileContentError("Unknow ship code '{code}'from '{file}'".format(code=platform_code,
                                                                                      file=netcdf_file_path))

    # write voyage specific attributes
    ncfile.title = ("IMOS SOOP Underway CO2 dataset measured onboard the %s "
                    "between the %s and %s") % (
                       vessel_name,
                       min(dtime).strftime(
                           "%d-%b-%Y %H:%M:%S"),
                       max(dtime).strftime("%d-%b-%Y %H:%M:%S"))
    ncfile.date_created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ncfile.abstract = (" This dataset contains underway CO2 measurements collected onboard the %s "
                       "between the %s and %s") % (vessel_name,
                                                   min(dtime).strftime(
                                                       "%d-%b-%Y %H:%M:%S"),
                                                   max(dtime).strftime("%d-%b-%Y %H:%M:%S"))

    ncfile.time_coverage_start = min(dtime).strftime("%Y-%m-%dT%H:%M:%SZ")
    ncfile.time_coverage_end = max(dtime).strftime("%Y-%m-%dT%H:%M:%SZ")
    ncfile.geospatial_lat_min = np.nanmin(np.array(dataf['GpsShipLatitude']))
    ncfile.geospatial_lat_max = np.nanmax(np.array(dataf['GpsShipLatitude']))
    ncfile.geospatial_lon_min = np.nanmin(np.array(dataf['GpsShipLongitude']))
    ncfile.geospatial_lon_max = np.nanmax(np.array(dataf['GpsShipLongitude']))
    ncfile.geospatial_vertical_min = 0.
    ncfile.geospatial_vertical_max = 0.
    ncfile.vessel_name = vessel_name
    ncfile.platform_code = platform_code

    ncfile.sourceFilename = os.path.basename(src_file)

    # add dimension and variables
    string_10_dim = 10  # max length of string TYPE across platform
    ncfile.createDimension('TIME', len(time))
    ncfile.createDimension('string_10', string_10_dim)
    # Choose to use PCtime /Date for TIME variable
    vartime = ncfile.createVariable('TIME', "d", 'TIME')
    latitude = ncfile.createVariable('LATITUDE', "d", 'TIME', fill_value=-999.)
    longitude = ncfile.createVariable(
        'LONGITUDE', "d", 'TIME', fill_value=-999.)
    data_type = ncfile.createVariable('TYPE', 'S1', ('TIME', 'string_10'))
    teq_raw = ncfile.createVariable('TEQ_raw', "f", 'TIME', fill_value=-999.)
    co2_std_value = ncfile.createVariable(
        'CO2_STD_Value', "f", 'TIME', fill_value=-999.)
    xco2_ppm_raw = ncfile.createVariable(
        'xCO2_PPM_raw', "f", 'TIME', fill_value=-999.)
    xh2o_ppt_raw = ncfile.createVariable(
        'xH2O_PPT_raw', "f", 'TIME', fill_value=-999.)
    # Need to use DryBoxdruck Pressure instead of LicorPress
    press_licor_raw = ncfile.createVariable(
        'Press_Licor_raw', "f", 'TIME', fill_value=-999.)
    diff_press_equ_raw = ncfile.createVariable(
        'Diff_Press_Equ_raw', "f", 'TIME', fill_value=-999.)
    h2o_flow_raw = ncfile.createVariable(
        'H2O_flow_raw', "f", 'TIME', fill_value=-999.)
    licor_flow_raw = ncfile.createVariable(
        'Licor_flow_raw', "f", 'TIME', fill_value=-999.)
    temp_raw = ncfile.createVariable(
        'TEMP_raw', "f", 'TIME', fill_value=-999.)  # IntakeShipTemp
    psal_raw = ncfile.createVariable('PSAL_raw', "f", 'TIME', fill_value=-999.)
    atmp_raw = ncfile.createVariable('ATMP_raw', "f", 'TIME', fill_value=-999.)
    wspd_raw = ncfile.createVariable('WSPD_raw', "f", 'TIME', fill_value=-999.)  # MetTrueWindSpKts
    wdir_raw = ncfile.createVariable('WDIR_raw', "f", 'TIME', fill_value=-999.)  # MetTrueWindDir
    tsg_flow_raw = ncfile.createVariable(
        'Tsg_flow_raw', "f", 'TIME', fill_value=-999.)
    temp_tsg_raw = ncfile.createVariable(
        'TEMP_Tsg_raw', "f", 'TIME', fill_value=-999.)

    if platform_code == 'VLMJ':
        labmain_sw_flow_raw = ncfile.createVariable(
            'LabMain_sw_flow_raw', "f", 'TIME', fill_value=-999.)

    # add IMOS standard global attributes and variable attributes

    ####TO ENABLE #generate_netcdf_att(ncfile, config_file, conf_file_point_of_truth=True)
    # set attribute value to variable type

    #for nc_var in [teq_raw, psal_raw, temp_raw, temp_tsg_raw]:
    #    nc_var.valid_max = np.float32(nc_var.valid_max)
    #    nc_var.valid_min = np.float32(nc_var.valid_min)

    # Set attribute 'units' type as string for variable whose type is interpreted as float by generate_netcdf_att
    #for nc_var in [co2_std_value, xco2_ppm_raw]:
    #    nc_var.units = '1e-6'

    #for nc_var in [xh2o_ppt_raw, psal_raw]:
    #    nc_var.units = '1e-3'
### END TO ENABLE
    # convert Wind speed to ms-1 before filling array with fillvalue
    dataf['MetTrueWindSpKts'] = dataf['MetTrueWindSpKts'].multiply(0.514444)

    # replace nans with fillvalue in dataframe
    dataf.fillna(value=float(-999.), inplace=True)
    # Can use either PCDate/Time or GPS. Decided to use PCDate /Time as it
    # simplifies the code
    vartime[:] = time

    latitude[:] = dataf['GpsShipLatitude'].values
    longitude[:] = dataf['GpsShipLongitude'].values

    # create fixed length strings padded with space
    # create variable of type string, then convert to array of char
    type_tmp = []

    for id in range(len(dataf['Type'])):
        type_tmp.append(dataf['Type'][id].ljust(string_10_dim))

    # convert to array of char
    type_tmp = stringtochar(np.array(type_tmp))
    data_type[:] = type_tmp
    teq_raw[:] = dataf['EquTemp'].values
    co2_std_value[:] = dataf['CO2StdValue'].values
    xco2_ppm_raw[:] = dataf['CO2um_m'].values
    xh2o_ppt_raw[:] = dataf['H2Omm_m'].values
    press_licor_raw[:] = dataf['DryBoxDruckPress'].values
    diff_press_equ_raw[:] = dataf['EquPress'].values
    h2o_flow_raw[:] = dataf['EquH2OFlow'].values
    licor_flow_raw[:] = dataf['LicorFlow'].values
    temp_raw[:] = dataf['IntakeShipTemp'].values
    # WSP converted to m s-1
    wspd_raw[:] = dataf['MetTrueWindSpKts'].values
    wdir_raw[:] = dataf['MetTrueWindDir'].values
    atmp_raw[:] = dataf['AtmSeaLevelPress'].values

    if platform_code == 'VLMJ':
        temp_tsg_raw[:] = dataf['TsgShipTemp'].values
        tsg_flow_raw[:] = dataf['TsgShipFlow'].values
        labmain_sw_flow_raw[:] = dataf['LabMainSwFlow'].values
        psal_raw[:] = dataf['TsgShipSalinity'].values
    elif platform_code == 'VNAA':
        temp_tsg_raw[:] = dataf['TsgSbe45Temp'].values
        psal_raw[:] = dataf['TsgSbe45Salinity'].values
        tsg_flow_raw[:] = dataf['SBE45Flow'].values

    ncfile.close()


def read_realtime_file(self):
    """
    Reads in data from realtime text files
    Cause input files have inconsistent number of column per line
    the function first reads file line by line into list, then create data frame
    Returns  : dataframe
               vessel_code_short
    """
    data = []

    # check that vessel specific prefix is valid
    platform_code_short = self.name[0:2]
    assert platform_code_short in VESSEL, "File name '%s' has unknown vessel_code" % self.name
    platform_code = VESSEL[platform_code_short]

    with open(self.src_path, 'r') as rt_file:
        header_txt_file = rt_file.readline()
        header_txt_file = (re.split(r'\t+', header_txt_file.rstrip('\r\n')))

        # create  an ordered dictionary of paramter name:indices
        headers = [(header_col, header_txt_file.index(header_col))
                   for header_col in header_txt_file]
        input_rt_parameter = collections.OrderedDict(headers)

        for line in rt_file:
            tmp_line = re.split(r'\t+', line.rstrip('\r\n'))
            if len(tmp_line) == len(input_rt_parameter):
                data.append(tmp_line)
            elif len(tmp_line) > 5 and len(tmp_line) < len(input_rt_parameter):
                line_filled_w_nans = fill_missing_with_nan(line.rstrip('\r\n'))
                line_filled_w_nans = re.split(r'\t+', line_filled_w_nans)
                data.append(line_filled_w_nans)
            else:
                continue

    # Convert list into array
    data_array = np.asarray(data)

    # array into dataframe
    dataf = pd.DataFrame(data_array, columns=input_rt_parameter.keys())
    # check parameters
    dataf = check_parameters(dataf, platform_code_short,
                             input_rt_parameter, self.src_path)

    return dataf, platform_code


def fill_missing_with_nan(line):
    """
    Solve issue with timesteps containing missing fields (case in Aurora files)
    Loop through occurences of matched pattern (here consisting of 2 consecutive tabs)
    and insert NaN between consecutive tabs. Since re.search looks for first location of pattern)
    insert, function iterate until expression does not produce a match
    """
    while re.search(r'\t\t', line) is not None:
        m = re.search(r'\t\t', line)
        re.sub(r'\t\t', line[:m.start() + 1] +
               'NaN' + line[m.end() - 1:], line)
        line = line[:m.start() + 1] + 'NaN' + line[m.end() - 1:]

    return line


def check_parameters(dataf, vessel_code, input_param, src_file):
    """
    Checks parameters list contains all required parameter(vessel specific)
    Cast selected parameter data to correct type
    Checks that Lat/Lon are not all missing.
    Returns updated dataframe
    """
    rt_input_parameters = set.union(INPUT_RT_PARAMETERS,
                                    eval(vessel_code + '_SPECIFIC_INPUT_PARAMS'))
    if not all(param in input_param for param in rt_input_parameters):
        missing_param = []
        for required_param in rt_input_parameters:
            if required_param not in input_param:
                missing_param = missing_param.append(required_param)
                raise InvalidFileContentError(
                    "Missing parameter(s) '{missing_param}' in file '{src_file}'.Aborting".format(
                        missing_param=missing_param, src_file=src_file))
    else:  # required_param all present . Change dtype to numeric where relevant
        # var TYPE conversion to string outside this function
        for param in rt_input_parameters:
            if param not in set(['Type', 'PcDate', 'PcTime']):
                dataf[param] = dataf[param].apply(pd.to_numeric, errors=coerce)

    if all(np.isnan(dataf['GpsShipLatitude'])) or all(np.isnan(dataf['GpsShipLongitude'])):
        raise InvalidFileContentError(
            "Latitude and/or Longitude values all missing in file '{src_file}'.Aborting".format(
                src_file=src_file))
    return dataf


if __name__ == '__main__':
    # call main function to generate to process RT files"
    netcdf_file_path = process_co2_rt()

    print netcdf_file_path
