import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from aodncore.pipeline import HandlerBase, PipelineFilePublishType, PipelineFile
from aodncore.util.misc import get_pattern_subgroups_from_string
from ncwriter import DatasetTemplate
from netCDF4 import date2num, Dataset

from ship_callsign import ship_callsign_list

SHIP_CODE = 'VLST'

SOOP_NRT_LOG_PATTERN = re.compile(r"""
                                  EPA_
                                  (?P<facility>SOOP_TMV1)_
                                  (?P<product_code>D2M|M2D|MEL|DEV)_.*
                                  \.log$
                                  """, re.VERBOSE)

NC_JSON_TEMPLATE_MOORING = os.path.join(os.path.dirname(__file__), 'soop_tmv_nrt_nc_template_mooring.json')
NC_JSON_TEMPLATE_TRAJECTORY = os.path.join(os.path.dirname(__file__), 'soop_tmv_nrt_nc_template_trajectory.json')


def parse_log_file(log_path):
    df = pd.read_csv(log_path, header=None,
                     engine='python')
    df.columns = ["TIME", "unknown1", "product_code", "unknown2", "LATITUDE", "LONGITUDE", "TEMP", "PSAL",
                  "CPHL", "TURB"]
    date_format = '%Y/%m/%d %H:%M:%S'
    df['TIME'] = pd.to_datetime(df['TIME'], format=date_format)

    df = df[np.isfinite(df['LATITUDE'])]
    df = df[np.isfinite(df['LONGITUDE'])]

    # force make time monotonic and time not duplicated
    df.set_index('TIME', inplace=True)
    df.sort_index(axis=0, inplace=True)
    df = df[~df.index.duplicated(keep='first')]
    return df


def netcdf_writer(log_path, output_dir):
    df = parse_log_file(log_path)
    ship_callsign_ls = ship_callsign_list()
    log_filename = os.path.basename(log_path)

    if SHIP_CODE not in ship_callsign_ls:
        raise ValueError(
            "Missing vessel callsign in file name '{name}'.".format(name=log_filename))

    if SOOP_NRT_LOG_PATTERN.match(log_filename):
        fields = get_pattern_subgroups_from_string(log_filename, SOOP_NRT_LOG_PATTERN)
        product_code = fields['product_code']

    if product_code in ['D2M', 'M2D']:
        product_type = "transect"
        featureType = "trajectory"
        template = DatasetTemplate.from_json(NC_JSON_TEMPLATE_TRAJECTORY)
    else:
        product_type = "mooring"
        featureType = "timeSeries"
        template = DatasetTemplate.from_json(NC_JSON_TEMPLATE_MOORING)

    template.global_attributes.update({
        'product_type': product_type})

    time_val_dateobj = date2num(df.index.to_pydatetime(),
                                template.variables['TIME']['units'],
                                template.variables['TIME']['calendar'])

    # replace all nan with FillValue from template value
    df.replace(np.nan, template.variables['LATITUDE']['_FillValue'], inplace=True)

    template.variables['TIME']['_data'] = time_val_dateobj
    template.variables['LATITUDE']['_data'] = df.LATITUDE.values
    template.variables['LONGITUDE']['_data'] = df.LONGITUDE.values

    template.variables['TEMP']['_data'] = df.TEMP.values
    template.variables['PSAL']['_data'] = df.PSAL.values
    template.variables['TURB']['_data'] = df.TURB.values
    template.variables['CPHL']['_data'] = df.CPHL.values

    if '1SecRaw' in log_filename:
        time_period = '1sec'
    else:
        time_period = '10secs'

    template.global_attributes.update({
        'time_coverage_start': df.index.strftime('%Y-%m-%dT%H:%M:%SZ')[0],
        'time_coverage_end': df.index.strftime('%Y-%m-%dT%H:%M:%SZ')[-1],
        'featureType': featureType,
        'date_created': pd.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'platform_code': SHIP_CODE,
        'vessel_name': ship_callsign_ls[SHIP_CODE],
        'geospatial_lat_min': df.LATITUDE.dropna().min(),
        'geospatial_lat_max': df.LATITUDE.dropna().max(),
        'geospatial_lon_min': df.LONGITUDE.dropna().min(),
        'geospatial_lon_max': df.LONGITUDE.dropna().max(),
        'time_period': time_period,
        'history': "File created %s" % pd.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    })

    nc_filename = 'IMOS_SOOP-TMV_TSUB_{time_start}_{vessel_code}_FV0{product_number}_{product_type}-{product_code}_END-{time_end}.nc'.format(
        time_start=df.index.strftime('%Y%m%dT%H%M%SZ')[0],
        time_end=df.index.strftime('%Y%m%dT%H%M%SZ')[-1],
        vessel_code=SHIP_CODE,
        product_number=0,
        product_type=product_type,
        product_code=product_code)

    netcdf_path = os.path.join(output_dir, nc_filename)
    template.to_netcdf(netcdf_path)
    return netcdf_path


class SoopTmvNrtHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopTmvNrtHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.log']

    def preprocess(self):
        f = self.file_collection[0]
        if f.extension == '.nc':
            # case where we repush an existing netcdf file
            f.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            f.dest_path = self.dest_path(f.src_path)

        elif f.extension == '.log':
            # case to create netcdf files from log files
            f.publish_type = PipelineFilePublishType.NO_ACTION

            log_path = self.file_collection[0].src_path
            netcdf_filepath = netcdf_writer(log_path, self.temp_dir)

            nc_file = PipelineFile(netcdf_filepath, dest_path=self.dest_path(netcdf_filepath))
            nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(nc_file)

    def dest_path(self, filepath):
        ship_callsign_ls = ship_callsign_list()
        soop_tmv_dir = os.path.join('IMOS', 'SOOP', 'SOOP-TMV',
                                    '%s_%s' %(SHIP_CODE, ship_callsign_ls[SHIP_CODE]),
                                    'realtime')

        with Dataset(filepath,  mode='r') as nc_obj:
            time_period = nc_obj.time_period
            product_type = nc_obj.product_type
            year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').year

        return os.path.join(soop_tmv_dir, product_type, time_period, '%d' % year, os.path.basename(filepath))
