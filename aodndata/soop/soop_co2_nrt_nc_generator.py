"""
# generate NetCDF file storing realtime SOOP-CO2 data.
# Script processes data from 2 vessels: RV Aurora Australis and RV Investigator
# -Extract variable relevant to CO2 measurements and processing from input text file.
# -Map vessel specific variable to set of common output variables
# Mapping as follows:
#       Input Variable                  NetCDF Variable
#        Investigator
#       PcDate+PcTime                        TIME
#       GpsShipLatitude                     LATITUDE
#       GpsShipLongitude                    LONGITUDE
#           Type                            TYPE
#           EquTemp                         TEQ_raw
#           CO2StdValue                     CO2_STD_Value
#           Li7815_CO2_avg                  xCO2_PPM_raw
#           Li7815_H2O_avg                  xH2O_PPM_raw
#           DryBoxDruckPress                Press_Licor_raw
#           EquPress                        Diff_Press_Equ_raw
#           EquH2OFlow                      H2O_flow_raw
#           LicorFlow                       Licor_flow_raw
#           AtmSeaLevelPress                ATMP_raw
#           MetTrueWindSpKts                WSPD_raw
#           MetTrueWindDir                  WDIR_raw
#           Intake_T1                        TEMP_1_raw
#           Intake_T2                        TEMP_2_raw
#           TsgShipSalinity                 PSAL_raw
#           TsgShipTemp                     TEMP_Tsg_raw
#           TsgShipFlow                     Tsg_flow_raw
#           LabMainSwFlow                   LabMain_sw_flow_raw
#           MetRelHum                       RELH_raw
#           MetAirTemp                      AIRT_raw
"""
import os
from datetime import datetime

import numpy as np
import pandas as pd
from aodncore.pipeline.exceptions import InvalidFileContentError
from aodntools.ncwriter import DatasetTemplate
from netCDF4 import stringtochar
from pkg_resources import resource_filename

VALID_PROJECT = ['IMOS', 'FutureReefMap', 'SOOP-CO2_RT']
INPUT_RT_PARAMETERS = {'Type', 'PcDate', 'PcTime', 'GpsShipLatitude',
                       'GpsShipLongitude', 'EquTemp', 'CO2StdValue',
                       'Li7815_CO2_avg', 'Li7815_H2O_avg', 'DryBoxDruckPress', 'EquPress',
                       'EquH2OFlow', 'LicorFlow', 'Intake_T1','Intake_T2', 'MetTrueWindSpKts',
                       'MetTrueWindDir', 'MetShipAtmPress','MetRelHum','MetAirTemp','TsgShipTemp',
                        'TsgShipSalinity', 'TsgShipFlow', 'LabMainSwFlow'}
VESSEL = {
    'IN': 'VLMJ'
}

NC_JSON_TEMPLATE = resource_filename("aodndata", "templates/soop_co2_nrt_nc_template.json")


def process_co2_rt(realtime_file, temp_dir, ship_callsign_ls):
    """
    Read in data from co2 realtime file and produce a netcdf file
    """
    # Parse data into dataframe
    (dataf, platform_code) = read_realtime_file(realtime_file)
    # format data
    (dtime, time) = get_time_formatted(dataf)

    netcdf_filename = create_netcdf_filename(platform_code, dtime)
    netcdf_file_path = os.path.join(temp_dir, "{filename}.nc").format(filename=netcdf_filename)

    netcdf_writer(netcdf_file_path, dataf, dtime, time, realtime_file.src_path, platform_code, ship_callsign_ls)

    return netcdf_file_path


def create_netcdf_filename(platform_code, dtime):
    """
    Generate filename
    """
    facility_param = 'IMOS_SOOP-CO2_GST'
    prodtype = 'FV00'
    time_start = min(dtime).strftime("%Y%m%dT%H%M%SZ")
    time_end = max(dtime).strftime("%Y%m%dT%H%M%SZ")
    filename = "{facility_param}_{time_start}_{platform_code}_{prodtype}_END-{time_end}".format(
        facility_param=facility_param,
        time_start=time_start,
        platform_code=platform_code,
        prodtype=prodtype,
        time_end=time_end
    )
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


def netcdf_writer(netcdf_file_path, dataf, dtime, time, src_file, platform_code, ship_callsign_ls):
    """
    Create the netcdf file
    """
    vessel_name = ship_callsign_ls[platform_code]
    template = DatasetTemplate.from_json(NC_JSON_TEMPLATE)

    # write voyage specific attributes
    template.global_attributes.update({
        'title': "IMOS SOOP Underway CO2 dataset measured onboard the %s "
                 "between the %s and %s" % (vessel_name,
                                            min(dtime).strftime("%d-%b-%Y %H:%M:%S"),
                                            max(dtime).strftime("%d-%b-%Y %H:%M:%S")),
        'date_created': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'history': 'file created on {date}'.format(date=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")),

        'abstract':  "This dataset contains underway CO2 measurements collected onboard the {vessel_name} "
                     "between the {start_date} and {end_date}".format(
            vessel_name=vessel_name,
            start_date=min(dtime).strftime("%d-%b-%Y %H:%M:%S"),
            end_date=max(dtime).strftime("%d-%b-%Y %H:%M:%S")),
        'time_coverage_start': min(dtime).strftime("%Y-%m-%dT%H:%M:%SZ"),
        'time_coverage_end': max(dtime).strftime("%Y-%m-%dT%H:%M:%SZ"),
        'geospatial_lat_min': np.nanmin(np.array(dataf['GpsShipLatitude'])),
        'geospatial_lat_max': np.nanmax(np.array(dataf['GpsShipLatitude'])),
        'geospatial_lon_min': np.nanmin(np.array(dataf['GpsShipLongitude'])),
        'geospatial_lon_max': np.nanmax(np.array(dataf['GpsShipLongitude'])),
        'geospatial_vertical_min': 0.,
        'geospatial_vertical_max': 0.,
        'vessel_name': vessel_name,
        'platform_code': platform_code,
        'sourceFilename': os.path.basename(src_file)
    })

    template.variables['WSPD_raw']['_data'] = dataf['MetTrueWindSpKts'].multiply(0.514444)

    # replace nans with fillvalue in dataframe
    dataf.fillna(value=float(-999.), inplace=True)
    # Can use either PCDate/Time or GPS. Decided to use PCDate /Time as it
    # simplifies the code
    template.variables['TIME']['_data'] = time
    template.variables['LATITUDE']['_data'] = dataf['GpsShipLatitude'].values
    template.variables['LONGITUDE']['_data'] = dataf['GpsShipLongitude'].values

    # create fixed length strings padded with space
    # create variable of type string, then convert to array of char
    string_10_dim = template.dimensions['string_10']

    # convert to array of char
    type_tmp = stringtochar(np.array(dataf['Type'], 'S{dimelen}'.format(dimelen=string_10_dim)))
    template.variables['TYPE']['_data'] = type_tmp

    template.variables['TEQ_raw']['_data'] = dataf['EquTemp'].values

    template.variables['CO2_STD_Value']['_data'] = dataf['CO2StdValue'].values
    template.variables['xCO2_PPM_raw']['_data'] = dataf['Li7815_CO2_avg'].values
    template.variables['xH2O_PPM_raw']['_data'] = dataf['Li7815_H2O_avg'].values
    template.variables['Press_Licor_raw']['_data'] = dataf['DryBoxDruckPress'].values
    template.variables['Diff_Press_Equ_raw']['_data'] = dataf['EquPress'].values
    template.variables['H2O_flow_raw']['_data'] = dataf['EquH2OFlow'].values
    template.variables['Licor_flow_raw']['_data'] = dataf['LicorFlow'].values
    template.variables['TEMP_1_raw']['_data'] = dataf['Intake_T1'].values
    template.variables['TEMP_2_raw']['_data'] = dataf['Intake_T2'].values
    template.variables['WSPD_raw']['_data'] = dataf['MetTrueWindSpKts'].values * 0.514444 # WSP converted to m s-1
    template.variables['WDIR_raw']['_data'] = dataf['MetTrueWindDir'].values
    template.variables['ATMP_raw']['_data'] = dataf['MetShipAtmPress'].values
    template.variables['TEMP_Tsg_raw']['_data'] = dataf['TsgShipTemp'].values
    template.variables['Tsg_flow_raw']['_data'] = dataf['TsgShipFlow'].values
    template.variables['LabMain_sw_flow_raw']['_data'] = dataf['LabMainSwFlow'].values
    template.variables['PSAL_raw']['_data']= dataf['TsgShipSalinity'].values
    template.variables['AIRT_raw']['_data'] = dataf['MetAirTemp'].values
    template.variables['RELH_raw']['_data'] = dataf['MetRelHum'].values

    template.to_netcdf(netcdf_file_path)
    return netcdf_file_path


def read_realtime_file(self):
    """
    Reads in data from realtime text files
    Cause input files have inconsistent number of column per line
    the function first reads file line by line into list, then create data frame
    Returns  : dataframe
               vessel_code_short
    """
    # check that vessel specific prefix is valid
    platform_code_short = self.name[0:2]
    assert platform_code_short in VESSEL, "File name '%s' has unknown vessel_code" % self.name
    platform_code = VESSEL[platform_code_short]

    dataf = pd.read_csv(self.src_path, sep='\t', error_bad_lines=False)
    dataf.drop(dataf.loc[dataf['Type'] == 'FILTER'].index, inplace=True)  # incorrect number of delimiter
    dataf.reset_index(inplace=True)
    input_rt_parameter = list(dataf)

    dataf = check_parameters(dataf, platform_code_short,
                             input_rt_parameter, self.src_path)
    dataf = dataf.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  # strip whitespace

    return dataf, platform_code


def check_parameters(dataf, vessel_code, input_param, src_file):
    """
    Checks parameters list contains all required parameter(vessel specific)
    Cast selected parameter data to correct type
    Checks that Lat/Lon are not all missing.
    Returns updated dataframe
    """
    missing_param = []
    if not all(param in input_param for param in INPUT_RT_PARAMETERS):
        for required_param in INPUT_RT_PARAMETERS:
            if required_param not in input_param:
                missing_param.append(required_param)
    else:  # required_param all present . Change dtype to numeric where relevant
        # var TYPE conversion to string outside this function
        for param in INPUT_RT_PARAMETERS:
            if param not in set(['Type', 'PcDate', 'PcTime']):
                dataf[param] = dataf[param].apply(pd.to_numeric, errors='coerce')  # convert bad non numeric to NaN

    if missing_param:
        raise InvalidFileContentError(
            "Missing parameter(s) '{missing_param}' in file '{src_file}'.Aborting".format(
                missing_param=missing_param, src_file=src_file))

    if all(np.isnan(dataf['GpsShipLatitude'])) or all(np.isnan(dataf['GpsShipLongitude'])):
        raise InvalidFileContentError(
            "Latitude and/or Longitude values all missing in file '{src_file}'.Aborting".format(
                src_file=src_file))
    return dataf


if __name__ == '__main__':
    # call main function to generate to process RT files"
    netcdf_file_path = process_co2_rt()

    print(netcdf_file_path)
