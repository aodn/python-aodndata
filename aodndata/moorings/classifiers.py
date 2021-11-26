import os
import re

from datetime import datetime as dt
from datetime import timedelta
from netCDF4 import Dataset

from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import (InvalidFileContentError, InvalidFileNameError, InvalidFileFormatError,
                                          InvalidInputFileError)


class MooringsFileClassifier(FileClassifier):
    """Classifier for moorings (DWM & ANMN) NetCDF files.
    """

    PROJECT = 'IMOS'

    SALINITY_VAR = {'PSAL', 'CNDC'}
    BGC_VAR = {'CPHL', 'CHLF', 'CHLU', 'FLU2', 'TURB', 'DOX1', 'DOX1_1', 'DOX2', 'DOXY', 'DOXS', 'CDOM', 'PAR'}
    VELOCITY_VAR = {'UCUR', 'VCUR', 'WCUR', 'UCUR_MAG', 'VCUR_MAG', 'CSPD'}
    WAVE_VAR = {'VAVH', 'SSDS', 'SSDS_MAG', 'SSWD', 'SSWD_MAG', 'SSWDT', 'SSWST', 'SSWV', 'SSWV_MAG', 'SSWVT', 'VAVT',
                'VDEN', 'VDEV', 'VDEP', 'VDES', 'VDIR', 'VDIR_MAG', 'VDIRT', 'WHTE', 'WHTH', 'WPFM', 'WPMH', 'WPSM',
                'WPTE', 'WPTH', 'WMPP', 'WMSH', 'WMXH', 'WPDI', 'WPDI_MAG', 'WPDIT', 'WPPE', 'WSMP', 'WSSH'}
    TEMP_VAR = {'PRES', 'PRES_REL', 'TEMP'}
    CO2_VAR = {'xCO2EQ_PPM', 'xCO2ATM_PPM', 'fCO2SW_UATM', 'DfCO2', 'TPH'}

    @classmethod
    def _get_data_category(cls, input_file):
        """Determine the category a file belongs to (Temperature,
        CTD_timeseires, Biogeochem_profile, etc..)

        """

        var_names = set(cls._get_variable_names(input_file))

        if var_names.intersection(cls.VELOCITY_VAR):
            return 'Velocity'

        if var_names.intersection(cls.WAVE_VAR):
            return 'Wave'

        if var_names.intersection(cls.CO2_VAR):
            return 'CO2'

        feature_type = cls._get_nc_att(input_file, 'featureType').lower()
        if feature_type == 'profile':
            if var_names.intersection(cls.BGC_VAR) or var_names.intersection(cls.SALINITY_VAR):
                return 'Biogeochem_profiles'
            else:
                raise InvalidFileContentError(
                    "Could not determine data category for '{name}'".format(name=input_file)
                )

        if feature_type == 'timeseries':
            if var_names.intersection(cls.BGC_VAR):
                return 'Biogeochem_timeseries'

            if var_names.intersection(cls.SALINITY_VAR):
                return 'CTD_timeseries'

        if feature_type == 'timeseriesprofile' and 'long-timeseries' in input_file:
            return 'aggregated_products'

        if var_names.intersection(cls.TEMP_VAR):
            return 'Temperature'

        raise InvalidFileContentError("Could not determine data category for '{name}'".format(name=input_file))

    @classmethod
    def _get_product_level(cls, input_file):
        """Determine the product level of the file, i.e. either 'non-QC' (FV00), 'burst-averaged'
        or 'gridded' (FV02 products), or empty for FV01 files.

        """
        name_field = cls._get_file_name_fields(input_file)

        if cls._get_data_category(input_file) == 'CO2':
            if 'realtime' in name_field[6]:
                return 'real-time'
            elif 'delayed' in name_field[6]:
                return 'delayed'
            else:
                raise InvalidFileNameError("Unknown CO2 file type '{input_file}'".format(input_file=input_file))

        if name_field[5] == 'FV00':
            return 'non-QC'

        if name_field[5] == 'FV02':
            if len(name_field) < 7:
                raise InvalidFileNameError(
                    "Can't determine product type from file name '{name}'".format(name=input_file)
                )
            if 'burst-averaged' in name_field[6]:
                return 'burst-averaged'
            if 'gridded' in name_field[6]:
                return 'gridded'

        return ''

    @classmethod
    def dest_path(cls, input_file):
        """
        Destination object path for a moorings netCDF file. Of the form:

          'IMOS/<facility>/<subfacility>/<site_code>/<data_category>/<product_level>'

        where
        <facility> = 'ANMN' or 'DWM'
        <subfacility> is the sub-facility code ('NRS', 'NSW', 'SOTS', etc...)
        <site_code> is the value of the site_code global attribute
        <data_category> is a broad category like 'Temperature', 'CTD_profiles', etc...
        <product_level> is
         - 'non-QC' for FV00 files
         - empty for FV01 files
         - 'burst-averaged' or 'gridded' as appropriate, for FV02 files
        The basename of the input file is appended.

        """
        name_fields = cls._get_file_name_fields(input_file)

        dir_list = [cls.PROJECT]
        dir_list.extend(cls._get_facility(input_file))

        if input_file.endswith('.nc'):
            dir_list.append(cls._get_site_code(input_file))
            dir_list.append(cls._get_data_category(input_file))
            dir_list.append(cls._get_product_level(input_file))
        elif input_file.endswith('.pdf'):
            site_code = name_fields[3]
            dir_list.extend([site_code, 'Field_logsheets'])
        elif input_file.endswith('.cnv'):
            site_code = name_fields[4]
            dir_list.extend([site_code, 'Biogeochem_profiles', 'non-QC', 'cnv'])
        elif input_file.endswith('.png'):
            platform_code = name_fields[2]
            site_code = platform_code.split('-')[0]  # remove '-ADCP' etc.
            dir_list.extend([site_code, 'plots'])
        else:
            raise InvalidFileFormatError(
                "Don't know where to put file '{name}' (unhandled extension)".format(name=input_file)
            )

        dir_list.append(os.path.basename(input_file))

        return cls._make_path(dir_list)


class DwmFileClassifier(MooringsFileClassifier):

    FACILITY = 'DWM'
    SOTS_IMAGES_ZIP_PATTERN = re.compile(r"images_[a-zA-Z0-9-]+-(?P<year>\d{4})\.zip$")
    SOTS_CALIBRATION_ZIP_PATTERN = re.compile(r"calibration_[a-zA-Z0-9-]+-(?P<year>\d{4})\.zip$")

   #old pipeline stuff
    WAVE_VAR = {'VAVH', 'HMAX', 'HAV'}
    MET_VAR = {'UWND', 'VWND', 'WDIR', 'WSPD', 'ATMP', 'AIRT', 'RELH', 'RAIN', 'RAIN_AMOUNT'}
    FLUX_VAR = {'H_RAIN', 'HEAT_NET', 'MASS_NET'}

    @classmethod
    def _get_old_data_category(cls, input_file):
        """Determine the category a file belongs to."""

        var_names = set(cls._get_variable_names(input_file))
        if var_names.intersection(cls.WAVE_VAR):
            return 'Surface_waves'

        if var_names.intersection(cls.FLUX_VAR):
            return 'Surface_fluxes'

        if var_names.intersection(cls.MET_VAR):
            return 'Surface_properties'

        raise InvalidFileContentError("Could not determine data category for {input_file}".format(input_file=input_file))


    @classmethod
    def _get_data_category(cls, input_file):
        """Determine the category a file belongs to (Temperature,
        CTD_timeseires, Velocity, etc..)

        """

        var_names = set(cls._get_variable_names(input_file))

        if var_names.intersection(cls.VELOCITY_VAR):
            return 'Velocity'

        if var_names.intersection(cls.BGC_VAR):
            return 'Biogeochem_timeseries'

        if var_names.intersection(cls.SALINITY_VAR):
            return 'CTD_timeseries'

        if var_names.intersection(cls.TEMP_VAR):
            return 'Temperature'

        raise InvalidFileContentError(
            "Could not determine data category for '{name}'".format(name=input_file)
        )

    @classmethod
    def _get_product_level(cls, input_file):
        """Determine the product level of the file, i.e. either 'real-time', or
        'non-QC' (delayed-mode FV00). Otherwise empty.

        """
        name_field = cls._get_file_name_fields(input_file)

        if 'realtime' in input_file:
            return 'real-time'

        if name_field[5] == 'FV00':
            return 'non-QC'

        return ''

    @classmethod
    def _get_deployment_year(cls, input_file):
        """
        For the given moorings data file, determine the year in which the deployment started.
        If the time_deployment_start attribute is missing, fall back on time_coverage_start.

        :param str input_file: full path to the file
        :return: Year of deployment
        :rtype: str

        """
        start_date = cls._get_nc_att(input_file, 'time_deployment_start', time_format=True, default='')
        if not start_date:
            start_date = cls._get_nc_att(input_file, 'time_coverage_start', time_format=True)
        year = start_date.year

        return year

    @classmethod
    def _is_realtime(cls, input_file):
        """
        Determine whether the given file contains real-time data based on:
        * the data_mode global attribute, if it exists;
        * the file name, if it contains the word 'realtime' or 'real-time'
          (case insensitive);
        * the time_coverage_start/end range (if it's shorter than a day).

        :param str input_file: name of the file
        :return: Whether the input file contains real-time data
        :rtype bool

        """
        data_mode = cls._get_nc_att(input_file, 'data_mode', default='')
        if data_mode == 'R':
            return True
        # Any other valid data mode is NOT real-time
        if data_mode in ('P', 'D', 'M'):
            return False

        file_name = os.path.basename(input_file)
        if re.search(r'real-?time', file_name, re.IGNORECASE):
            return True

        time_start = cls._get_nc_att(input_file, 'time_coverage_start', time_format=True)
        time_end = cls._get_nc_att(input_file, 'time_coverage_end', time_format=True)
        if (time_end - time_start) <= timedelta(days=1):
            return True

        return False

    @classmethod
    def dest_path(cls, input_file):
        """
        Destination object path for an DWM file. Of the form:

          'IMOS/DWM/DA/<platform_code>/<data_category>/<product_level>'
          or
          'IMOS/DWM/SOTS/<year_of_deployment>/<product_type>'
          or
          'IMOS/DWM/SOTS/calibration'
          or
          'IMOS/DWM/SOTS/images'

        where
        <platform_code> is the value of the platform_code global attribute
        <data_category> is a broad category like 'Temperature', 'CTD_profiles', etc...
        <product_level> is
         - 'non-QC' for FV00 files
         - empty for FV01 files
        <year_of_deployment> is the year in which the deployment started
        <product_type> is
         - 'real-time';
         - empty (for delayed mode data)

        The basename of the input file is appended.

        """
        dir_list = [cls.PROJECT, cls.FACILITY]
        input_file_basename = os.path.basename(input_file)

        # deal with image zip files first, as they are simpler
        if cls.SOTS_IMAGES_ZIP_PATTERN.match(input_file_basename):
            dir_list.extend(['SOTS', 'images', input_file_basename])
            return cls._make_path(dir_list)
        
        # deal with calibration files that contain pdf files
        if cls.SOTS_CALIBRATION_ZIP_PATTERN.match(input_file_basename):
            dir_list.extend(['SOTS', 'calibration', input_file_basename])
            return cls._make_path(dir_list)

        fac, subfac = cls._get_facility(input_file)
        is_asfs_and_rt = subfac == 'ASFS' and cls._is_realtime(input_file)
        if 'FV02_hourly-depth-gridded-product' in input_file_basename:
            dir_list.append(subfac)
            dir_list.append('CSIRO_gridded_all_variables')
        elif subfac == 'DA':
            dir_list.append(subfac)
            dir_list.append(cls._get_nc_att(input_file, 'platform_code'))
            dir_list.append(cls._get_data_category(input_file))
            dir_list.append(cls._get_product_level(input_file))
        elif is_asfs_and_rt: # rt files with old names not migrated yet
            cat = cls._get_old_data_category(input_file)
            start_time = cls._get_nc_att(input_file,'time_coverage_start',time_format=True)
            rt_folder_name = '{}_daily'.format(start_time.year)
            dir_list += ['ASFS', 'SOFS', cat, 'Real-time', rt_folder_name]
        elif subfac in ('SOTS', 'ASFS'):
            dir_list.append('SOTS')
            dir_list.append(cls._get_deployment_year(input_file))
            if cls._is_realtime(input_file):
                dir_list.append('real-time')
        else:
            raise InvalidFileNameError(
                "Unknown DWM sub-facility '{subfac}' for file '{input_file}'".format(subfac=subfac,
                                                                                      input_file=input_file)
            )

        dir_list.append(input_file_basename)

        return cls._make_path(dir_list)


def dest_path_anmn_nrs_realtime(filepath):
    """Returns the relative path a given netCDF file should be published to, based on the name and content of the file.
    Only works for ANMN NRS real-time files.

    :param filepath: full path of the file
    :return: relative destination path including file name
    """

    filename = os.path.basename(filepath)

    # Start with base path for this sub-facility
    path_list = ['IMOS', 'ANMN', 'NRS', 'REAL_TIME']

    # add site code
    with Dataset(filepath, mode='r') as f:
        site_code = getattr(f, 'site_code', '')
    if not site_code:
        raise InvalidFileContentError("File '{name}' has no site_code attribute!".format(name=filename))
    path_list.append(site_code)

    # add product sub-directory
    if re.match('IMOS_ANMN-NRS_MT_.*-Surface-.*-MET', filename):
        path_list.append('Meteorology')
    elif re.match('IMOS_ANMN-NRS_W_.*-Surface-.*-wave', filename):
        path_list.append('Wave')
    elif re.match('IMOS_ANMN-NRS_TPSOBUE_.*-SubSurface-.*-WQM', filename):
        path_list.append('Biogeochem_timeseries')
    else:
        raise InvalidInputFileError(
            "File name '{name}' doesn't match pattern for any known NRS real-time product".format(name=filename)
        )

    path_list.append(filename)

    return os.path.join(*path_list)
