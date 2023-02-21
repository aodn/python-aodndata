#!/usr/bin/env python3
import os
import pandas as pd
import shapely.geometry
import shapely.wkt

def create_empty_dataframe():
    """
    create empty dataframe from a dict with data types

    Same as the hourly_timeseries.py for the moorings product

    :param: variable name and variable type. List of tuples
    :return: empty dataframe
    """
    # create empty dataframe with dtypes
    columns = [('tag_deployment_id', str),
               ('transmitter_id', str),
               ('species', str),
               ('tagging_project', str),
               ('time_coverage_start', str),
               ('time_coverage_end', str),
               ('geom_df', str),
               ('url', str),
               ('size', int),
               ]
    df_index_tmp = pd.DataFrame({k: pd.Series(dtype=t) for k, t in columns})

    return df_index_tmp


# MAIN FUNCTION
def extract_metadata(input_file, destination_s3):
    """
    create a dataframe from a single csv file (tag file) from the file collection

    :param:
           input_file: path to the input file
           destination_s3: destination path (url)

    :return: dataframe with file metadata
    """
    # create an empty dictionary
    df_csv_extract = {}

    # read each csv files
    df_csv = pd.read_csv(input_file.local_path, parse_dates=['detection_datetime'])  # loads the entire csv in memory
    df_csv_1 = df_csv.iloc[0]

    # fill in the dictionary
    df_csv_extract['tag_deployment_id'] = df_csv_1['transmitter_id'] + '-' \
                                          + str(df_csv_1['tag_id']) + '-' \
                                          + str(df_csv_1['transmitter_deployment_id'])
    df_csv_extract['transmitter_id'] = df_csv_1['transmitter_id']
    df_csv_extract['species'] = df_csv_1['species_common_name']
    df_csv_extract['tagging_project'] = df_csv_1['tagging_project_name']
    df_csv_extract['time_coverage_start'] = df_csv['detection_datetime'].min()
    df_csv_extract['time_coverage_end'] = df_csv['detection_datetime'].max()

    # creates a geometry using unique detection location points
    coords_all = list(zip(df_csv.receiver_recovery_longitude, df_csv.receiver_recovery_latitude))
    coords = list(set(coords_all))
    # TODO: when upgrading to shapely 2+, geometry.MultiPoint has to be called differently
    df_csv_extract['geom_df'] = shapely.geometry.MultiPoint(coords).wkt  # to plot the detection points on the WMS
    df_csv_extract['url'] = destination_s3
    df_csv_extract['size'] = [os.path.getsize(input_file.local_path)]
    df_csv_extract_df = pd.DataFrame.from_dict(df_csv_extract)

    return df_csv_extract_df
