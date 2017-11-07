import os
import re

from netCDF4 import Dataset

from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import (InvalidFileContentError, InvalidFileNameError, InvalidFileFormatError,
                                          InvalidInputFileError)


class MooringsFileClassifier(FileClassifier):
    """Classifier for moorings (ABOS & ANMN) NetCDF files.
    """

    PROJECT = 'IMOS'

    SALINITY_VAR = {'PSAL', 'CNDC'}
    BGC_VAR = {'CPHL', 'CHLF', 'CHLU', 'FLU2', 'TURB', 'DOX1', 'DOX1_1', 'DOX2', 'DOXY', 'DOXS'}
    VELOCITY_VAR = {'UCUR', 'VCUR', 'WCUR', 'UCUR_MAG', 'VCUR_MAG', 'CSPD'}
    WAVE_VAR = {'VAVH', 'SSDS', 'SSDS_MAG', 'SSWD', 'SSWD_MAG', 'SSWDT', 'SSWST', 'SSWV', 'SSWV_MAG', 'SSWVT', 'VAVT',
                'VDEN', 'VDEV', 'VDEP', 'VDES', 'VDIR', 'VDIR_MAG', 'VDIRT', 'WHTE', 'WHTH', 'WPFM', 'WPMH', 'WPSM',
                'WPTE', 'WPTH', 'WMPP', 'WMSH', 'WMXH', 'WPDI', 'WPDI_MAG', 'WPDIT', 'WPPE', 'WSMP', 'WSSH'}
    TEMP_VAR = {'PRES', 'PRES_REL', 'TEMP'}

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
        <facility> = 'ANMN' or 'ABOS'
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