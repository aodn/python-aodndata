import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from aodncore.pipeline import HandlerBase, PipelineFilePublishType, PipelineFile
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string
from ncwriter import DatasetTemplate
from netCDF4 import date2num, Dataset
from pkg_resources import resource_filename

from ship_callsign import ship_callsign_list

SHIP_CODE = 'VLST'
SOOP_NRT_LOG_PATTERN = re.compile(r"""
                                  EPA_
                                  (?P<facility>SOOP_TMV1)_
                                  (?P<product_code>D2M|M2D|MEL|DEV|M2S|S2M|SYD)_.*
                                  \.log$
                                  """, re.VERBOSE)

NC_JSON_TEMPLATE_MOORING = resource_filename("aodndata", "templates/soop_tmv_nrt_nc_template_mooring.json")
NC_JSON_TEMPLATE_TRAJECTORY = resource_filename("aodndata", "templates/soop_tmv_nrt_nc_template_trajectory.json")


def parse_log_file(log_path):
    df = pd.read_csv(log_path, header=None,
                     engine='python')
    df.columns = ["TIME", "status_flag", "product_code", "distance_from_port_km",
                  "LATITUDE", "LONGITUDE", "TEMP", "PSAL", "CPHL", "TURB"]

    try:
        date_format = '%Y/%m/%d %H:%M:%S'
        df['TIME'] = pd.to_datetime(df['TIME'], format=date_format)
    except ValueError, e:
        date_format = '%d/%m/%Y %H:%M:%S'
        df['TIME'] = pd.to_datetime(df['TIME'], format=date_format)

    df = df[np.isfinite(df['LATITUDE'])]
    df = df[np.isfinite(df['LONGITUDE'])]

    # force make time monotonic and time not duplicated
    df.set_index('TIME', inplace=True)
    df.sort_index(axis=0, inplace=True)
    df = df[~df.index.duplicated(keep='first')]
    return df


def netcdf_writer(log_path, output_dir, ship_name):
    df = parse_log_file(log_path)
    log_filename = os.path.basename(log_path)

    fields = get_pattern_subgroups_from_string(log_filename, SOOP_NRT_LOG_PATTERN)
    product_code = fields['product_code']

    if product_code in ['D2M', 'M2D', 'S2M', 'M2S']:
        product_type = "transect"
        feature_type = "trajectory"
        template = DatasetTemplate.from_json(NC_JSON_TEMPLATE_TRAJECTORY)
    elif product_code in ['DEV', 'MEL', 'SYD']:
        product_type = "mooring"
        feature_type = "timeSeries"
        template = DatasetTemplate.from_json(NC_JSON_TEMPLATE_MOORING)
    else:
        raise InvalidFileNameError(
            "SOOP NRT input logfile has incorrect product_code '{product_code}'. Not belonging to any of "
            "('D2M', 'M2D', 'S2M', 'M2S','DEV', 'MEL', 'SYD').".format(product_code=product_code))

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

    time_period = '1sec' if '1SecRaw' in log_filename else '10secs'

    template.global_attributes.update({
        'time_coverage_start': df.index.strftime('%Y-%m-%dT%H:%M:%SZ')[0],
        'time_coverage_end': df.index.strftime('%Y-%m-%dT%H:%M:%SZ')[-1],
        'featureType': feature_type,
        'date_created': pd.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'platform_code': SHIP_CODE,
        'vessel_name': ship_name,
        'geospatial_lat_min': df.LATITUDE.dropna().min(),
        'geospatial_lat_max': df.LATITUDE.dropna().max(),
        'geospatial_lon_min': df.LONGITUDE.dropna().min(),
        'geospatial_lon_max': df.LONGITUDE.dropna().max(),
        'time_period': time_period,
        'history': "File created {date_created}".format(
            date_created=pd.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
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
        self.allowed_extensions = ['.nc', '.log', '.zip']
        self.ship_callsign_ls = None

    def preprocess(self):
        if self.custom_params is not None and self.custom_params.get('ship_callsign_ls'):
            self.ship_callsign_ls = self.custom_params['ship_callsign_ls']
        else:
            self.ship_callsign_ls = ship_callsign_list()

        if SHIP_CODE not in self.ship_callsign_ls:
            raise RuntimeError(
                "Missing vessel callsign {callsign} from vocabulary'.".format(callsign=SHIP_CODE))

        f = self.file_collection[0]

        if f.extension == '.nc':
            # case where we re-push an existing netcdf file
            f.publish_type = PipelineFilePublishType.HARVEST_UPLOAD

        elif f.extension == '.log':
            log_filename = os.path.basename(f.src_path)

            if SOOP_NRT_LOG_PATTERN.match(log_filename) is None:
                raise InvalidFileNameError(
                    "SOOP NRT input logfile has incorrect naming '{name}'.".format(name=log_filename))

            # case to create netcdf files from log files
            f.publish_type = PipelineFilePublishType.NO_ACTION

            netcdf_filepath = netcdf_writer(f.src_path, self.temp_dir, self.ship_callsign_ls[SHIP_CODE])

            nc_file = PipelineFile(netcdf_filepath)
            nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            self.file_collection.add(nc_file)

    def dest_path(self, filepath):
        soop_tmv_dir = os.path.join('IMOS', 'SOOP', 'SOOP-TMV',
                                    '{ship_code}_{ship_name}'.format(ship_code=SHIP_CODE,
                                                                     ship_name=self.ship_callsign_ls[SHIP_CODE]),
                                    'realtime')

        with Dataset(filepath,  mode='r') as nc_obj:
            time_period = nc_obj.time_period
            product_type = nc_obj.product_type
            year = datetime.strptime(nc_obj.time_coverage_start, '%Y-%m-%dT%H:%M:%SZ').year

        return os.path.join(soop_tmv_dir, product_type, time_period, '%d' % year, os.path.basename(filepath))
