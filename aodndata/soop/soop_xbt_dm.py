from __future__ import absolute_import
from __future__ import unicode_literals
import datetime
import itertools
import os
import tempfile

from matplotlib.pyplot import (plot, savefig, subplots, subplots_adjust, text,
                               title, xticks)
from netCDF4 import Dataset, num2date
from numpy import ma

from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType


class SoopXbtDmHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SoopXbtDmHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.jpg']

    def preprocess(self):
        jpg_output_path, jpg_output_dest_path = create_plot(self.file_collection[0].src_path, self.temp_dir)
        jpg_file = PipelineFile(jpg_output_path, dest_path=jpg_output_dest_path)
        jpg_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY
        self.file_collection.add(jpg_file)

    @staticmethod
    def dest_path(filepath):
        F = Dataset(filepath, mode='r')
        xbt_line = F.XBT_line
        xbt_line_description = F.XBT_line_description
        date_start = datetime.datetime.strptime(F.time_coverage_start, "%Y-%m-%dT%H:%M:%SZ")
        year_line = date_start.strftime('%Y')
        F.close()

        soop_xbt_dm_path = os.path.join('IMOS', 'SOOP', 'SOOP-XBT', 'DELAYED')

        # case for 'indian-ocean' 'tasman-sea' and 'SO_Southern-Ocean'
        if xbt_line.startswith("PX") or xbt_line.startswith("IX"):
            xbt_line = "Line_%s_%s" % (xbt_line, xbt_line_description)

        return os.path.join(soop_xbt_dm_path, xbt_line, str(year_line), os.path.basename(filepath))


def create_plot(netcdfFilePath, output_dir):
    """ create plot to be ingested in SOOP XBT NRT pipeline"""
    F = Dataset(netcdfFilePath, 'r', format='NETCDF4')
    cruise_id = F.XBT_cruise_ID
    sea_water_temperature = F.variables['TEMP']
    depth = F.variables['DEPTH']
    time = F.variables['TIME']
    time = num2date(time[:], time.units, time.calendar)
    lat = F.variables['LATITUDE'][:]
    lon = F.variables['LONGITUDE'][:]
    xbt_unique_id = F.XBT_uniqueid

    # Load only the data which does not have a quality control value equal to qcFlag and greater than good_flag
    bad_flag = 4
    good_flag = 1
    i_good_data = (F.variables['TEMP_quality_control'][:] != bad_flag) & (
        F.variables['TEMP_quality_control'][:] >= good_flag)
    temp_values = sea_water_temperature[:]
    depth_values = depth[:]

    # Modify the values which we don't want to plot to replace them with the Fillvalue
    temp_values[~i_good_data] = sea_water_temperature._FillValue

    # new XBT files dont have a FillValue att for DEPTH since DEPTH is a
    # dimension. However previous files do. Need to handle both case if we do
    # some reprocessing
    if hasattr(depth, '_FillValue'):
        depth_values[~i_good_data] = depth._FillValue
        depth_values = ma.masked_values(depth_values, F.variables['DEPTH']._FillValue)

    # Modify the mask in order to change the boolean, since some previous non Fillvalue data are now Fillvalue
    temp_values = ma.masked_values(temp_values, F.variables['TEMP']._FillValue)

    fig, ax1 = subplots(figsize=(13, 9.2), dpi=80, facecolor='w', edgecolor='k')
    subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)

    ax1.set_xlabel(sea_water_temperature.long_name + ' in ' + sea_water_temperature.units)
    ax1.set_ylabel(depth.long_name + ' in ' + depth.units)

    try:
        if all(temp_values.mask):
            text(0.5, 0.5, 'No Good Data available', color='r',
                 fontsize=20,
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax1.transAxes)
        else:
            plot(temp_values[:], -depth_values[:])
    except:
        plot(temp_values[:], -depth_values[:])

    ax1.set_ylim(-1100, 0)
    xticks([-3, 0, 5, 10, 15, 20, 25, 30, 35])

    date_start = datetime.datetime.strptime(F.time_coverage_start, "%Y-%m-%dT%H:%M:%SZ").strftime(
        "%Y-%m-%d %H:%M:%S UTC")
    title(F.title + '\n Cruise  ' + cruise_id + '-' + F.XBT_line_description +
          ' - XBT id ' + str(xbt_unique_id) + '\nlocation ' + "%0.2f" % lat +
          ' S ; ' + "%0.2f" % lon + ' E\n' + date_start, fontsize=10)

    F.close()
    jpg_output = tempfile.NamedTemporaryFile(delete=False, dir=output_dir)
    savefig(jpg_output)

    jpg_dest_path = '{}{}'.format(os.path.splitext(SoopXbtDmHandler.dest_path(netcdfFilePath))[0], '.jpg')
    return jpg_output.name, jpg_dest_path
