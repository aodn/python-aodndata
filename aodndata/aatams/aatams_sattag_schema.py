"""This module defines the Aatams Satellite Tag QC Schema class and their respective
functions."""
import os
from datetime import datetime
from functools import partial
import logging

from schema import And, Or, Schema, Use, SchemaError

from aodndata.common.csv_schema import CSVSchema


logger = logging.getLogger(__name__)

AATAMS_DIALECT_CSV = {"delimiter": ",", "strict": True}

VALIDATION_MSG = "\tValidating cross columns references from {file0}[{field0}] against {file1}[{field1}]"
CROSS_CONTENT_FAIL_MSG = "Cross content comparison failed for value: {setdiff}.\n\
        {file0}[{field0}] = {value0}\n\
        while \n\
        {file1}[{field1}] = {value1}."
INCONSISTENT_CAMPAIGNS = "Filename campaign id {file_cid} is inconsistent with CSV ids: {csv_cids}"


AATAMS_QC_NUMBER_OF_FILES_IN_ZIP = 7
AATAMS_QC_FILE_TYPE_NAMES = (
    "metadata",
    "ctd",
    "diag",
    "dive",
    "haulout",
    "ssmoutputs",
    "summary",
)

DATE_FMT_STR_1 = "%Y-%m-%dT%H:%M:%SZ"


# schema functions -> Return arg or False
def valid_wmo_device(astr):
    """Check if a valid wmo device.

    Args:
      astr: a wmo device string

    Returns:
      str: astr if valid
      bool: False if invalid

    """
    return astr if isinstance(astr, str) else False


def valid_tag_type(astr):
    """Check if a valid tag type.

    Args:
      astr: a tag type string

    Returns:
      str: astr if valid
      bool: False if invalid

    """
    return astr if isinstance(astr, str) else False


def valid_longitude(afloat):
    """Check if a valid longitude.

    Args:
      afloat: a longitude number

    Returns:
      float: afloat if valid
      bool: False if invalid

    """
    valid = -180.0 <= afloat <= 180.0
    return afloat if valid else False


def valid_latitude(afloat):
    """Check if a valid latitude.

    Args:
      afloat: a latitude number

    Returns:
      float: afloat if valid
      bool: False if invalid

    """
    valid = -90 <= afloat <= 90.0
    return afloat if valid else False


# Transform functions -> Return mutations
def not_applicable(astr):
    """Check string for emptiness, not applicable or NaN string.

    Args:
      astr: a string

    Returns:
      str: "" if empty, not applicable or NaN

    Raises:
        ValueError if astr is valid input.

    """
    if astr.strip().lower() in ("", "na", "nan"):
        return ""
    raise ValueError("entry {astr} is valid".format(astr=astr))


def str2list(astr, delimiter=","):
    """Split string by a delimiter.

    Args:
      astr: a string
      delimiter: a string delimiter

    Returns:
      list: A list of str splits

    """
    return astr.split(delimiter)


def iter_int(alist):
    """Transform every list item into integer.

    Args:
      alist: A list

    Returns:
      list: a list of integers

    Raises:
      ValueError: if an item cannot be an int.

    """
    return [int(x) for x in alist]


def iter_float(alist):
    """Transform every list item into float.

    Args:
      alist: A list

    Returns:
      list: a list of floats

    Raises:
      ValueError: if an item cannot be an float.

    """
    return [float(x) for x in alist]


def str2date(astr, fmt):
    """Convert a string to datetime object.

    Args:
      astr: A string
      fmt: A datetime.strptime format string

    Returns:
      datetime: the datetime representation

    """
    try:
        return datetime.strptime(astr, fmt)
    except ValueError:
        return datetime.strptime(astr.replace("24:00:00", "00:00:00"), fmt)


# check functions -> return bool or false
def check_len_list(alen, alist):
    """Check the length of a list.

    Args:
      alen: list len
      alist: a list

    Returns:
      bool: True or False

    """
    return alen == len(alist)


def check_csv_tablename(table_names, csv_filenames):
    """Check if a list of AATAMS csv file names
    contains the specific table strings in their
    names.

    [table_name]_[campaign]_[mode].csv

    Args:
      table_names[list,set]: names to match in csv_filenames
      csv_filenames[list,set]: AATAMS csv file names

    Returns:
      bool: True or False

    """
    expected = set(table_names)
    received = {os.path.basename(x).split("_")[0] for x in csv_filenames}
    return expected == received


def check_csv_campaign_name(csv_filenames):
    """Check if a list of AATAMS csv file names
    contains the same campaign string in their
    names.

    [table_name]_[campaign]_[mode].csv

    Args:
      csv_filenames[list,set]: AATAMS csv file names

    Returns:
      bool: True or False

    """
    campaigns = (get_campaign(x) for x in csv_filenames)
    return len(set(campaigns)) == 1


def is_positive(anumber):
    """Check positiveness.

    Args:
      a number: a number

    Returns:
      bool: True or False

    """
    return anumber >= 0


def is_negative(anumber):
    """Check negativeness.

    Args:
      a number: a number

    Returns:
      bool: True or False

    """
    return anumber <= 0


def is_equal(x, y):
    """Check equality between two items.

    Args:
      x: something
      y: something else

    Returns:
      bool: True or False

    """
    return x == y


def get_metadata_from_filename(filestr):
    """Get the qc mode and campaign
    from a aatams zip file.

    Args:
      filestr: the zipfile name/path

    Returns:
      mode[str]: 'dm' or 'nrt'
      campaign[str]: campaign id

    Raises:
      ValueError: if file is not a aatams file
    """
    name, extension = os.path.splitext(filestr)
    if extension not in ('.zip', '.csv'):
        raise ValueError("{} is not a zip or csv file.".format(filestr))

    mode = name.split('_')[-1]
    not_dm_or_nrt = mode not in ('dm', 'nrt')
    if not_dm_or_nrt:
        raise ValueError("Invalid AATAMS file {}: qc mode is not 'dm' or 'nrt'.".format(filestr))
    campaign = name.split('_')[-2]
    return mode, campaign


def get_campaign(filestr):
    return get_metadata_from_filename(filestr)[1]

def check_number_of_files_is_correct(alist):
    return check_len_list(AATAMS_QC_NUMBER_OF_FILES_IN_ZIP,alist)

def check_name_of_csv_files_is_correct(files):
    return check_csv_tablename(AATAMS_QC_FILE_TYPE_NAMES,files)

# Schema dicts & cases
FILENAMES_IN_ZIP_SCHEMA = And(
    check_number_of_files_is_correct,
    check_name_of_csv_files_is_correct,
    check_csv_campaign_name,
    error="Zip file content is invalid. Check if the number, name, and campaign of csv files are correct.")

CSV_SEX_CLASS = str  # Or("f", "m", "female", "male")
CSV_AGE_CLASS = str  # Or("adult", "subadult", "juvenile")

CSV_DATE_ISO = Use(partial(str2date, fmt=DATE_FMT_STR_1))
CSV_EMPTY = Use(not_applicable)

CSV_INT = Use(int)
CSV_POSITIVE_INT = And(CSV_INT, is_positive)
CSV_NEGATIVE_INT = And(CSV_INT, is_negative)
CSV_LIST = Use(partial(str2list, delimiter=AATAMS_DIALECT_CSV["delimiter"]))
CSV_LIST_OF_INT = And(CSV_LIST, iter_int)

CSV_FLOAT = Use(float)
CSV_POSITIVE_FLOAT = And(CSV_FLOAT, is_positive)
CSV_NEGATIVE_FLOAT = And(CSV_FLOAT, is_negative)
CSV_LIST_OF_FLOAT = And(CSV_LIST, iter_float)

# match 0 otherwise schema fails since 0 is false
CSV_LONGITUDE = And(CSV_FLOAT, Or(valid_longitude, 0), error="Invalid longitude input")
CSV_LATITUDE = And(CSV_FLOAT, Or(valid_latitude, 0))  # as above

METADATA_SCHEMA = {
    "sattag_program": str,
    "device_id": str,
    "ptt": CSV_INT,
    "body": CSV_INT,
    "device_wmo_ref": valid_wmo_device,
    "tag_type": valid_tag_type,
    "common_name": str,
    "species": str,
    "release_longitude": CSV_LONGITUDE,
    "release_latitude": CSV_LATITUDE,
    "release_site": str,
    "release_date": Or(CSV_EMPTY, CSV_DATE_ISO),
    "recovery_date": Or(CSV_EMPTY, CSV_DATE_ISO),
    "age_class": CSV_AGE_CLASS,
    "sex": Or(CSV_EMPTY, CSV_SEX_CLASS),
    "length": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "estimated_mass": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "actual_mass": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "state_country": str,
    "qc_start_date": Or(CSV_EMPTY, CSV_DATE_ISO),
    "qc_end_date": Or(CSV_EMPTY, CSV_DATE_ISO)
}

COORD_SCHEMA = {
    "lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    "ssm_lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    "ssm_lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "ssm_x": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_y": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_x_se": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_y_se": str,  # Or(CSV_EMPTY, CSV_FLOAT),
}

POS_SCHEMA = {
    "x": Or(CSV_EMPTY, CSV_FLOAT),
    "y": Or(CSV_EMPTY, CSV_FLOAT),
    "x_se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "y_se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "u": Or(CSV_EMPTY, CSV_FLOAT),
    "v": Or(CSV_EMPTY, CSV_FLOAT),
    "u_se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "v_se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "s": Or(CSV_EMPTY, CSV_FLOAT),
    "s_se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
}

CTD_SCHEMA = {
    "ref": METADATA_SCHEMA["device_id"],
    "ptt": METADATA_SCHEMA["ptt"],
    "end_date": Or(CSV_DATE_ISO),
    "max_dbar": CSV_POSITIVE_FLOAT,
    "num": CSV_INT,
    "n_temp": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "n_cond": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "n_sal": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "temp_dbar": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "temp_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "cond_dbar": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "cond_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "sal_dbar": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "sal_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "n_fluoro": Or(CSV_EMPTY, CSV_INT),
    "fluoro_dbar": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "fluoro_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "n_oxy": Or(CSV_EMPTY, CSV_INT),
    "oxy_dbar": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "oxy_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "qc_profile": CSV_INT,
    "qc_temp": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "qc_sal": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "sal_corrected_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "created": Or(CSV_DATE_ISO),
    "modified": Or(CSV_DATE_ISO),
    "n_photo": Or(CSV_EMPTY, CSV_INT),
    "photo_dbar": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "photo_vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    **COORD_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

DIAG_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "d_date": Or(CSV_DATE_ISO),
    "lq": CSV_INT,
    "lat": CSV_LATITUDE,
    "lon": CSV_LONGITUDE,
    "alt_lat": CSV_LATITUDE,
    "alt_lon": CSV_LONGITUDE,
    "n_mess": CSV_FLOAT,
    "n_mess_120": CSV_FLOAT,
    "best_level": CSV_FLOAT,
    "pass_dur": CSV_INT,
    "freq": CSV_POSITIVE_FLOAT,
    "v_mask": CSV_FLOAT,
    "alt": Or(CSV_EMPTY, CSV_FLOAT),
    "est_speed": Or(CSV_EMPTY, CSV_FLOAT),
    "km_from_home": Or(CSV_EMPTY, CSV_FLOAT),
    "iq": CSV_INT,
    "nops": str,  # CSV_INT,
    "deleted": str,  # CSV_EMPTY,
    "actual_ptt": str,  # CSV_INT,
    "error_radius": str,  # CSV_INT,
    "semi_major_axis": str,  # CSV_INT,
    "semi_minor_axis": str,  # CSV_INT,
    "ellipse_orientation": str,  # CSV_INT,
    "hdop": str,  # CSV_INT,
    "satellite": str,
    "diag_id": CSV_INT,
    "ssm_lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    "ssm_lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "ssm_x": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_y": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_x_se": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_y_se": str,  # Or(CSV_EMPTY, CSV_FLOAT),
    "cid": METADATA_SCHEMA["sattag_program"],
}

DIVE_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "cnt": CSV_POSITIVE_INT,
    "de_date": Or(CSV_DATE_ISO),
    "surf_dur": CSV_FLOAT,
    "dive_dur": CSV_FLOAT,
    "max_dep": CSV_POSITIVE_FLOAT,
    **{"d" + str(x): Or(CSV_EMPTY, CSV_POSITIVE_FLOAT) for x in range(1, 5)},
    **{"v" + str(x): Or(CSV_EMPTY, CSV_FLOAT) for x in range(1, 6)},
    "travel_r": Or(CSV_EMPTY, CSV_FLOAT),
    "homedist": Or(CSV_EMPTY, CSV_FLOAT),
    "bottom": Or(CSV_EMPTY, CSV_FLOAT),
    **{"t" + str(x): CSV_FLOAT for x in range(1, 5)},
    "d_speed": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "n_depths": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "n_speeds": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "depth_str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "speed_str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "propn_str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "percent_area": Or(CSV_EMPTY, CSV_FLOAT),
    "residual": CSV_POSITIVE_INT,
    "grp_number": CSV_POSITIVE_INT,
    "d5": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),  # wtf...
    "t5": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "degc_str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "illum_str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    **{
        x: Or(CSV_EMPTY, CSV_POSITIVE_INT)
        for x in [
            "pca_desc",
            "pca_btm",
            "pca_asc",
            "pca_max_desc",
            "pca_max_btm",
            "pca_max_asc",
            "pca_mean_desc",
            "pca_mean_btm",
            "pca_mean_asc",
        ]
    },
    **{
        x: Or(CSV_EMPTY, CSV_POSITIVE_FLOAT)
        for x in ["swim_eff_desc", "swim_eff_btm", "swim_eff_asc", "swim_eff_whole"]
    },
    **{
        x: Or(CSV_EMPTY, CSV_POSITIVE_INT)
        for x in [
            "secs_desc",
            "secs_btm",
            "secs_asc",
        ]
    },
    **{
        x: Or(CSV_EMPTY, CSV_FLOAT)
        for x in [
            "pitch_desc",
            "pitch_btm",
            "pitch_asc",
        ]
    },
    "pitch_str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "tagging_id": Or(CSV_EMPTY, CSV_INT),
    "de_date_tag": Or(CSV_EMPTY, CSV_DATE_ISO),
    "qc": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    **{"d" + str(x): Or(CSV_EMPTY, CSV_POSITIVE_FLOAT) for x in range(6, 26)},
    **{"t" + str(x): Or(CSV_EMPTY, CSV_POSITIVE_FLOAT) for x in range(6, 26)},
    "ds_date": Or(CSV_DATE_ISO),
    "start_lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "start_lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    **COORD_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

HAULOUT_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "s_date": Or(CSV_DATE_ISO),
    "e_date": Or(CSV_DATE_ISO),
    "haulout_number": CSV_INT,
    "cnt": CSV_POSITIVE_INT,
    "phosi_secs": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "wet_n": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "wet_min": Or(CSV_EMPTY, CSV_FLOAT),
    "wet_max": Or(CSV_EMPTY, CSV_FLOAT),
    "wet_mean": Or(CSV_EMPTY, CSV_FLOAT),
    "wet_sd": Or(CSV_EMPTY, CSV_FLOAT),
    "tagging_id": Or(CSV_EMPTY, CSV_INT),
    "s_date_tag": Or(CSV_EMPTY, CSV_DATE_ISO),
    "e_date_tag": Or(CSV_EMPTY, CSV_DATE_ISO),
    "end_number": CSV_INT,
    **COORD_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

SSMOUTPUTS_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "date": Or(CSV_DATE_ISO),
    "lon": COORD_SCHEMA["lon"],
    "lat": COORD_SCHEMA["lat"],
    **POS_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

SUMMARY_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "cnt": CSV_POSITIVE_INT,
    "s_date": Or(CSV_DATE_ISO),
    "e_date": Or(CSV_DATE_ISO),
    "div_dist": Or(CSV_EMPTY, CSV_FLOAT),
    "surf_tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "dive_tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "haul_tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "n_cycles": CSV_POSITIVE_INT,
    "av_depth": CSV_FLOAT,
    "max_depth": CSV_FLOAT,
    "cruise_tm": str,  # ignore
    "avg_sst": str,  # ignore
    "avg_speed": str,  # ignore
    "sd_depth": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "av_dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd_dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max_dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_n_cycles": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_av_depth": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_max_depth": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_avg_speed": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_sd_depth": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_av_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_sd_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_max_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_dive_tm": str,  # Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "av_surf_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd_surf_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max_surf_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_av_surf_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_sd_surf_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp_max_surf_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "pca": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "swim_eff_desc": str,  # Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "swim_eff_asc": str,  # Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "swim_eff_whole": str,  # Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "secs_desc": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "secs_asc": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "pitch_desc": str,  # Or(CSV_EMPTY, CSV_INT),
    "pitch_asc": str,  # Or(CSV_EMPTY, CSV_INT),
    "av_haulout_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd_haulout_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max_haulout_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "av_phosi_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd_phosi_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max_phosi_dur": str,  # Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "tagging_id": Or(CSV_EMPTY, CSV_INT),
    "s_date_tag": Or(CSV_EMPTY, CSV_DATE_ISO),
    "e_date_tag": Or(CSV_EMPTY, CSV_DATE_ISO),
    "ssm_lon": COORD_SCHEMA["ssm_lon"],
    "ssm_lat": COORD_SCHEMA["ssm_lat"],
    "ssm_x": COORD_SCHEMA["ssm_x"],
    "ssm_y": COORD_SCHEMA["ssm_y"],
    "ssm_x_se": COORD_SCHEMA["ssm_x_se"],
    "ssm_y_se": COORD_SCHEMA["ssm_y_se"],
    "cid": METADATA_SCHEMA["sattag_program"],
}


class AatamsSattagQcSchema(CSVSchema):
    """The AATAMS SATTAG QC SCHEMA class.

    This is a schema class for validation
    of AATAMS csv files.

    The class inherit properties from
    CSVSchema to be able to open ,load and
    validate headers and columns.

    The workflow can be defined in three states:

    1. Validation of the zip file (see zip_content_schema)
    2. Validation of the metadata file - headers/fields (see file_schemas)
    3. Validation of all other files - headers/fields (see file_schemas)
    4. Validation of cross references among files (see cross_validation_scope_list)
    5. Validation of the CID/Sattag_program/Campaign ids

    """

    @staticmethod
    def file2schema(file_str):
        """Generate the schema name from the filename.

        Args:
          file_str: filename.

        Returns:
          str: The schema name string.

        """
        return os.path.basename(file_str).split("_")[0]

    def __init__(self, skip_every=0, bulk_load=True, dialect_csv=None):
        """Initialize the class with CSV reading options.

        skip_every: integer to skip every n line in the csv
        bulk_load: boolean to read the entire csv in memory

        """
        super().__init__(skip_every=skip_every, bulk_load=bulk_load,dialect_csv=dialect_csv)

        # self.manifest_schema = ...
        self.zip_content_schema = FILENAMES_IN_ZIP_SCHEMA

        self.file_schemas = {
            "metadata": METADATA_SCHEMA,
            "ctd": CTD_SCHEMA,
            "diag": DIAG_SCHEMA,
            "dive": DIVE_SCHEMA,
            "haulout": HAULOUT_SCHEMA,
            "ssmoutputs": SSMOUTPUTS_SCHEMA,
            "summary": SUMMARY_SCHEMA,
        }

        self.cross_validation_scope_list = [
            {
                "metadata": "sattag_program",
                "ctd": "cid",
                "diag": "cid",
                "dive": "cid",
                "haulout": "cid",
                "ssmoutputs": "cid",
                "summary": "cid",
            },
        ]
        self.headers = {}
        self.metadata = {}
        self.ctd = {}
        self.diag = {}
        self.dive = {}
        self.haulout = {}
        self.ssmoutputs = {}
        self.summary = {}


    def validate_zip_names(self, file_list):
        """Validate the file names.

        Args:
          file_list: a list of file names.

        Returns:
          Any: The result of schema call.

        Raises:
          SchemaError: If the zip files are non-conformant.

        """
        logger.info("Validating filename conventions")
        return Schema(self.zip_content_schema).validate(file_list)

    def validate_headers_only(self, file_list):
        """Validate the headers of a list of csv files.

        Args:
          file_list: a list of csv files.

        Returns:
          Dict[str,Any]: A dictionary with the result of the schema call
          for every file header.

        Raises:
          SchemaError: if any header is non-conformant.

        """
        headers = {}
        for file in file_list:
            schema_name = self.file2schema(file)
            schema = self.file_schemas[schema_name]
            logger.info("Loading headers in %s" % file)
            header = self.load_csv_header(file)
            logger.info("Validating headers in %s" % file)
            headers[schema_name] = self.validate_header(header, schema)
        return headers

    def cross_set_validation(self, scope_list):
        """Perform cross validation of column values across different file types. The
        validation is done by comparing the sets of different columns across the
        different file/data types.

        For example, comparison of the set(metadata['sattag_program'])
        against the set(ctd['cid']).

        Args:
          scope_dict: A list of cross validation dict scopes

        Returns:
          column_set_generator: a generator with column sets.

        Raises:
          SchemaError: if cross validatiton fails.

        """
        if not scope_list:
            logger.info("Cross validation skipped")
            return

        logger.info("Validating cross references")
        for cvdict in scope_list:
            filetypes = list(cvdict.keys())
            datanames = list(cvdict.values())

            filetype0 = filetypes.pop(0)
            dataname0 = datanames.pop(0)
            xset = set(getattr(self, filetype0)[dataname0])

            for filetype, dataname in zip(filetypes, datanames):
                logger.info(
                    VALIDATION_MSG.format(
                        file0=filetype0,
                        field0=dataname0,
                        file1=filetype,
                        field1=dataname,
                    )
                )
                yset = set(getattr(self, filetype)[dataname])
                isdiff = xset.symmetric_difference(yset)
                if isdiff:
                    errmsg = CROSS_CONTENT_FAIL_MSG.format(
                        setdiff=isdiff,
                        file0=filetype,
                        field0=dataname,
                        value0=xset,
                        file1=filetype0,
                        field1=dataname0,
                        value1=yset,
                    )
                    raise SchemaError(errmsg)
                else:
                    yield xset

    def quick_validation(self, file_list):
        """Perform validation for the csv files,
        and their headers.

        Args:
          file_list: a list of csv files.

        Returns:
          None: if all valid

        Raises:
          SchemaError: if zip or headers are non-conformant.

        """
        self.validate_zip_names(file_list)
        self.validate_headers_only(file_list)

    def extensive_validation(self, file_list):
        """Extensive validation of files within a AATAMS zip.

        1. Filename conventions
        2. Metadata headers
        3. Data rows types
        4. Data rows relationships
        5. Data rows cross relationships with the metadata
        6. SATTAG_PROGRAM/CIDs are unique and match Campaign in filenames.

        Args:
          file_list: a list of csv files.

        Returns:
          None: if all files are conformant.

        Raises:
          SchemaError: if zip, headers, types and content are non-conformant.

        """
        self.validate_zip_names(file_list)
        schema_name = "metadata"
        metadata_file = [x for x in file_list if self.file2schema(x) == schema_name]

        self.headers["metadata"], self.metadata = self.validate_file(metadata_file[0])

        for file in file_list:
            schema_name = self.file2schema(file)
            header, valid_data = self.validate_file(file)
            logger.info("Validation ended for %s" % file)
            self.headers[schema_name] = header
            setattr(self, schema_name, valid_data)

        #Since we validate/cross-check cid/sattag_programs, reuse the computations
        content_sets = list(self.cross_set_validation(self.cross_validation_scope_list))
        campaigns_from_content = content_sets[0]
        campaigns_from_filenames = {get_campaign(x) for x in file_list}
        inconsistent_campaigns = campaigns_from_content != campaigns_from_filenames
        if inconsistent_campaigns:
            errmsg = INCONSISTENT_CAMPAIGNS.format(file_cid=campaigns_from_filenames,
                    csv_cids=campaigns_from_content)
            raise SchemaError(errmsg)
