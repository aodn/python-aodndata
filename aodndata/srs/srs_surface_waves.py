import os
import re
import tempfile
from datetime import datetime

import cartopy as cart
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, FileType
from aodncore.pipeline.exceptions import InvalidFileNameError
from aodncore.util.misc import get_pattern_subgroups_from_string

ALTI_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00'
ALTI_VALID_SATS = ["CRYOSAT-2",
                   "ENVISAT",
                   "ERS-1",
                   "ERS-2",
                   "GEOSAT",
                   "GFO",
                   "HY-2",
                   "JASON-1",
                   "JASON-2",
                   "JASON-3",
                   "SARAL",
                   "SENTINEL-3A",
                   "SENTINEL-3B",
                   "TOPEX"
                   ]
ALTI_FILE_PATTERN = re.compile(r"""
                            IMOS_SRS-Surface-Waves_MW_
                            (?P<platform_code>{})_FV02_
                            (?P<latitude>[0-9]{{3}})
                            (?P<latitude_dir>(S|N))-
                            (?P<longitude>[0-9]{{3}})E-
                            DM00\.nc$
                            """.format('|'.join(ALTI_VALID_SATS)), re.VERBOSE)

SCAT_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/Wind-Scatterometry-DM00'
SCAT_VALID_SATS = ["ERS-1",
                   "ERS-2",
                   "QUIKSCAT",
                   "METOP-A",
                   "OCEANSAT-2",
                   "METOP-B",
                   "METOP-C",
                   "RAPIDSCAT"
                   ]
SCAT_FILE_PATTERN = re.compile(r"""
                            IMOS_SRS-Surface-Waves_M_Wind-
                            (?P<platform_code>{})_FV02_
                            (?P<latitude>[0-9]{{3}})
                            (?P<latitude_dir>(S|N))-
                            (?P<longitude>[0-9]{{3}})E-
                            DM00\.nc$
                            """.format('|'.join(SCAT_VALID_SATS)), re.VERBOSE)

SAR_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/SAR'

SAR_FILE_PATTERN = re.compile(r"""
                              IMOS_SRS-Surface-Waves_W_
                              (?P<nc_time_cov_start>[0-9]{8}T[0-9]{6}Z)_
                              (?P<platform_code>Sentinel-1A|Sentinel-1B)_
                              (?P<qc_level>FV00|FV01_DM00)_
                              (?P<wavenum>K1|K2)_END-
                              (?P<nc_time_cov_end>[0-9]{8}T[0-9]{6}Z)\.nc$
                              """, re.VERBOSE)

SAR_WIND_PREFIX_PATH = 'IMOS/SRS/Surface-Waves/SAR_Wind'

SAR_WIND_FILE_PATTERN = re.compile(r"""
                              IMOS_SRS-Surface-Waves_M_
                              (?P<nc_time_cov_start>[0-9]{8})_Coastal-Wind-
                              (?P<platform_code>Sentinel-1A|Sentinel-1B)_
                              (?P<qc_level>FV00|FV01_DM00)-
                              (?P<absolute_orbit_number>.*)-
                              (?P<data_take_id_hex>.*)-
                              (?P<product_id_hex>.*)
                              \.nc$
                              """, re.VERBOSE)


def dest_path_srs_surface_waves(filepath):
    file_basename = os.path.basename(filepath)
    if ALTI_FILE_PATTERN.match(file_basename):
        return dest_path_alt_scat_common(filepath, ALTI_FILE_PATTERN, ALTI_PREFIX_PATH)
    elif SCAT_FILE_PATTERN.match(file_basename):
        return dest_path_alt_scat_common(filepath, SCAT_FILE_PATTERN, SCAT_PREFIX_PATH)
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))


def dest_path_alt_scat_common(filepath, file_pattern, prefix_path):
    file_basename = os.path.basename(filepath)
    if file_pattern.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, file_pattern)
        lat = int(fields['latitude'])
        lon = int(fields['longitude'])
        lat_dir = fields['latitude_dir']

        def round_down_div(val, divisor=20):
            """ return div rounded value of a value"""
            return val - (val % divisor)

        if lat_dir == 'S':
            lat_bottom_left = round_down_div(lat) + 20
        elif lat_dir == 'N':
            lat_bottom_left = round_down_div(lat)

        lon_bottom_left = round_down_div(lon)

        coord_dirname = '{lat_bottom_left}{lat_dir}_{lon_bottom_left}E'.format(
            lat_bottom_left=str(lat_bottom_left).zfill(3),
            lon_bottom_left=str(lon_bottom_left).zfill(3),
            lat_dir=lat_dir)

    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))

    return os.path.join(prefix_path, fields['platform_code'], coord_dirname, file_basename)


def dest_path_srs_surface_waves_sar(filepath, file_pattern=SAR_FILE_PATTERN, prefix_path=SAR_PREFIX_PATH):
    file_basename = os.path.basename(filepath)
    if file_pattern.match(file_basename):
        fields = get_pattern_subgroups_from_string(file_basename, file_pattern)
        sat = fields['platform_code']
        qc_level = fields['qc_level']
    else:
        raise InvalidFileNameError(
            "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                filename=os.path.basename(filepath)))

    if "FV00" in qc_level:
        qc_level_str = "REALTIME"
    elif "FV01" in qc_level:
         qc_level_str = "DELAYED"

    nc_time_cov_start = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%dT%H%M%SZ')

    path = os.path.join(prefix_path, qc_level_str, sat.upper(),
                        '%d' % nc_time_cov_start.year, '%02d' % nc_time_cov_start.month,
                        file_basename)
    return path


class SrsSarWindHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(SrsSarWindHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.png', '.manifest']

    def preprocess(self):
        """
        Creation of a plot for each NetCDF file
        :return:
        """
        nc_files = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)

        for nc_file in nc_files:

            png_output_path, png_output_dest_path = create_sar_wind_plot(nc_file.src_path, self.temp_dir)
            png_file = PipelineFile(png_output_path, dest_path=png_output_dest_path)
            png_file.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            self.file_collection.add(png_file)

    @staticmethod
    def dest_path(filepath, file_pattern=SAR_WIND_FILE_PATTERN, prefix_path=SAR_WIND_PREFIX_PATH):
        file_basename = os.path.basename(filepath)
        if file_pattern.match(file_basename):
            fields = get_pattern_subgroups_from_string(file_basename, file_pattern)
            sat = fields['platform_code']
            qc_level = fields['qc_level']
        else:
            raise InvalidFileNameError(
                "file name: \"{filename}\" not matching regex to deduce dest_path".format(
                    filename=os.path.basename(filepath)))

        if "FV00" in qc_level:
            qc_level_str = "REALTIME"
        elif "FV01" in qc_level:
             qc_level_str = "DELAYED"

        nc_time_cov_start = datetime.strptime(fields['nc_time_cov_start'], '%Y%m%d')

        path = os.path.join(prefix_path, qc_level_str, sat.upper(),
                            '%d' % nc_time_cov_start.year, '%02d' % nc_time_cov_start.month,
                            '%02d' % nc_time_cov_start.day, file_basename)
        return path


def create_sar_wind_plot(netcdfFilePath, output_dir):
    """ create plot to be ingested in SRS SAR WIND pipeline"""

    def to_uv(ws, phi):
        '''
        Here phi needs to be the math angle of wind
        relative to east and positive anti-clockwise
        can be 0-360 or +-180, I think it doesn't matter
        as the function internally handles it
        e.g. to_uv(10, -45) == to_uv(10, 360-45)
        or.  to_uv(10, -90) == to_uv(10, 270)
        '''
        u = ws * np.cos(np.deg2rad(phi))
        v = ws * np.sin(np.deg2rad(phi))
        return u, v

    def met2math(wdir_met):
        '''
        meteorological wdir is the from direction rel. to North
        source: http://colaweb.gmu.edu/dev/clim301/lectures/wind/wind-uv
        '''
        return (270. - wdir_met) % 360.

    # Set contour colors, levels, land color etc.
    contour_clrs = np.array(([212, 212, 212],
                             [170, 170, 170],
                             [129, 129, 129],
                             [88, 88, 88],
                             [181, 209, 228],
                             [127, 165, 199],
                             [73, 121, 170],
                             [20, 77, 141],
                             [177, 220, 173],
                             [126, 179, 130],
                             [75, 138, 87],
                             [25, 97, 45],
                             [254, 253, 174],
                             [245, 186, 129],
                             [237, 119, 84],
                             [229, 52, 39],
                             [246, 10, 29],
                             [190, 57, 194])) / 255.0
    levels = np.array((0, 1, 2, 3, 4, 5, 6.5, 8, 9.5, 11, 12.5, 14, 15.5, 17.5, 19.5, 21.5, 25, 30))
    land_clr = (247 / 255, 206 / 255, 160 / 255)
    mps2knots = 1.944

    with xr.open_dataset(netcdfFilePath, decode_times=False) as dset:

        min_lon = dset.attrs['geospatial_lon_min']
        max_lon = dset.attrs['geospatial_lon_max']
        min_lat = dset.attrs['geospatial_lat_min']
        max_lat = dset.attrs['geospatial_lat_max']

        extent = (min_lon - 0.5, max_lon + 0.5, max_lat + 0.5, min_lat - 0.5)

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(50, 50),
                                 subplot_kw={'projection': cart.crs.PlateCarree()}, sharey=True)
        ax = axes[0]
        land_10m = cfeature.NaturalEarthFeature('physical', 'land', '10m')
        ax.add_feature(land_10m, edgecolor='k', facecolor=land_clr, linewidth=2)
        ax.set_extent(extent)

        ax.contourf(dset['LONGITUDE'], dset['LATITUDE'], dset['WSPD_CAL'],
                    levels=levels, transform=cart.crs.PlateCarree(), extend='max', colors = contour_clrs)

        gl = ax.gridlines(draw_labels=True, linestyle='--')
        gl.xlabel_style = {'color': 'grey', 'weight': 'bold', 'size': 20}
        gl.ylabel_style = {'color': 'grey', 'weight': 'bold', 'size': 20}

        # Add arrows to show the wind vectors
        fact = 15
        slc = slice(None, None, fact)

        uv = to_uv(dset['WSPD_CAL'] * mps2knots, met2math(dset['WDIR']))
        u = uv[0]
        v = uv[1]
        ax.barbs(dset['LONGITUDE'].isel(TIME=slc, RANGE=slc),
                 dset['LATITUDE'].isel(TIME=slc, RANGE=slc),
                 u.isel(TIME=slc, RANGE=slc),
                 v.isel(TIME=slc, RANGE=slc),
                 pivot='middle', transform=cart.crs.PlateCarree(),
                 color='k', rounding=True)
        ax.set_title('Calibrated SAR wind speed and direction', fontsize=30)

        ax = axes[1]
        land_10m = cfeature.NaturalEarthFeature('physical', 'land', '10m')
        ax.add_feature(land_10m, edgecolor='k', facecolor=land_clr, linewidth=2)
        ax.set_extent(extent)

        cs = ax.contourf(dset['LONGITUDE'], dset['LATITUDE'], dset['WSPD_ECMWF'],
                         levels=levels, transform=cart.crs.PlateCarree(), extend='max', colors = contour_clrs)
        gl = ax.gridlines(draw_labels=True, linestyle='--')
        gl.xlabel_style = {'color': 'grey', 'weight': 'bold', 'size': 20}
        gl.ylabel_style = {'color': 'grey', 'weight': 'bold', 'size': 20}

        # Add arrows to show the wind vectors
        fact = 15
        slc = slice(None, None, fact)

        uv = to_uv(dset['WSPD_ECMWF'] * mps2knots, met2math(dset['WDIR_ECMWF']))
        u = uv[0]
        v = uv[1]
        ax.barbs(dset['LONGITUDE'].isel(TIME=slc, RANGE=slc),
                 dset['LATITUDE'].isel(TIME=slc, RANGE=slc),
                 u.isel(TIME=slc, RANGE=slc),
                 v.isel(TIME=slc, RANGE=slc),
                 pivot='middle', transform=cart.crs.PlateCarree(),
                 color='k', rounding=True)
        ax.set_title('ECMWF wind speed and direction', fontsize=30)
        ax.tick_params(axis='x', labelsize=30)

        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="5%", pad=1.5, axes_class=plt.Axes)

        fig.add_axes(ax_cb)

        cbar = plt.colorbar(cs, ax=axes, orientation='vertical',
                            label='wind speed (m s-1)', aspect=15,
                            shrink=0.25,cax=ax_cb)

        cbar.ax.tick_params(labelsize=30)
        cbar.set_label(label='wind speed (m s-1)', size=30)
        cbar.set_ticks(levels)
        cbar.set_ticklabels(levels)

        img_output = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix='.png')
        plt.savefig(img_output, format='png', bbox_inches='tight')

        ax.clear()
        fig.clf()
        plt.close(fig)

        png_dest_path = '{}{}'.format(os.path.splitext(SrsSarWindHandler.dest_path(netcdfFilePath))[0], '.png')
        return img_output.name, png_dest_path
