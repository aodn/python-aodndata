import os
from datetime import datetime
from functools import partial

from schema import And, Or, Schema, Use

from .csv_schema import CSVSchema

AATAMS_DM_NUMBER_OF_FILES_IN_ZIP = 7
AATAMS_DM_FILE_TYPE_NAMES = (
    "metadata",
    "ctd",
    "diag",
    "dive",
    "haulout",
    "ssmoutputs",
    "summary",
)

DATE_FMT_STR_1 = "%Y-%m-%dT%H:%M:%SZ"
DATE_FMT_STR_2 = "%m/%d/%y %H:%M:%S"


# schema functions -> Return arg or False
def valid_device(astr):  # TODO expand to particular devices fmts?
    """Check if a valid device.

    Args:
      astr: a device string

    Returns:
      str: astr if valid
      bool: False if invalid

    """
    return astr if len(astr.split("-")) >= 3 else False


def valid_wmo_device(astr):  # TODO expand to particular codes?
    """Check if a valid wmo device.

    Args:
      astr: a wmo device string

    Returns:
      str: astr if valid
      bool: False if invalid

    """
    return astr if astr[0] == "Q" else False


def valid_tag_type(astr):  # TODO expand to particular strings.
    """Check if a valid tag type.

    Args:
      astr: a tag type string

    Returns:
      str: astr if valid
      bool: False if invalid

    """
    return astr if "_" in astr else False


def valid_longitude(afloat):  # TODO check convention
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


def not_applicable(astr):  # TODO: handle every case as particular?
    """Check string for emptiness, not applicable or NaN string.

    Args:
      astr: a string

    Returns:
      str: "" if valid
      bool: False if invalid

    """
    if astr in ("", "NA", "NaN"):
        return ""
    else:
        return False


# Transform functions -> Return mutations


def str2list(astr, delimiter):
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
    [int(x) for x in alist]


def iter_float(alist):
    """Transform every list item into float.

    Args:
      alist: A list

    Returns:
      list: a list of floats

    Raises:
      ValueError: if an item cannot be an float.

    """
    [float(x) for x in alist]


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


def check_file_names(file_names, flist):
    """Check if filenames are present in a full path file list.

    Args:
      file_names: a list of file names
      flist: a list of full path file names

    Returns:
      bool: True or False

    """
    ngroup0 = set(file_names)
    ngroup1 = set([os.path.basename(x).split("_")[0] for x in flist])
    return ngroup0 == ngroup1


def is_positive(anumber):
    """Check positiveness.

    Args:
      anumber: a number

    Returns:
      bool: True or False

    """
    return anumber > 0


def is_negative(anumber):
    """Check negativeness.

    Args:
      anumber: a number

    Returns:
      bool: True or False

    """
    return anumber < 0


def is_equal(x, y):
    """Check equality between two items.

    Args:
      x: something
      y: something else

    Returns:
      bool: True or False

    """
    return True if x == y else False


check_number_of_files_is_correct = partial(
    check_len_list, AATAMS_DM_NUMBER_OF_FILES_IN_ZIP
)
check_name_of_files_is_correct = partial(check_file_names, AATAMS_DM_FILE_TYPE_NAMES)

# Schema dicts & cases
FILENAMES_IN_ZIP_SCHEMA = And(
    check_number_of_files_is_correct, check_name_of_files_is_correct
)

CSV_SEX_CLASS = Or("f", "m")
CSV_AGE_CLASS = Or("adult", "subadult", "juvenile")

CSV_DATE_ISO = Use(partial(str2date, fmt=DATE_FMT_STR_1))
CSV_DATE_US = Use(partial(str2date, fmt=DATE_FMT_STR_2))
CSV_EMPTY = Use(not_applicable)

CSV_INT = Use(int)
CSV_POSITIVE_INT = And(CSV_INT, is_positive)
CSV_NEGATIVE_INT = And(CSV_INT, is_negative)
CSV_LIST = Use(str2list)
CSV_LIST_OF_INT = And(Use(str2list), iter_int)

CSV_FLOAT = Use(float)
CSV_POSITIVE_FLOAT = And(CSV_FLOAT, is_positive)
CSV_NEGATIVE_FLOAT = And(CSV_FLOAT, is_negative)
CSV_LIST_OF_FLOAT = And(Use(str2list), iter_float)

# match 0 otherwise schema fails since 0 is false
CSV_LONGITUDE = And(CSV_FLOAT, Or(valid_longitude, 0))
CSV_LATITUDE = And(CSV_FLOAT, Or(valid_latitude, 0))  # as above

METADATA_SCHEMA = {
    "sattag_program": str,  # TODO
    "device_id": valid_device,
    "ptt": CSV_INT,
    "body": str,  # TODO
    "device_wmo_ref": valid_wmo_device,
    "tag_type": valid_tag_type,  # TODO
    "common_name": str,  # TODO
    "species": str,  # TODO
    "release_longitude": CSV_LONGITUDE,
    "release_latitude": CSV_LATITUDE,
    "release_site": str,  # TODO
    "release_date": Or(CSV_EMPTY, CSV_DATE_ISO, CSV_DATE_US),
    "recovery_date": Or(CSV_EMPTY, CSV_DATE_ISO, CSV_DATE_US),
    "age_class": CSV_AGE_CLASS,  # TODO not applicable is case!?
    "sex": CSV_SEX_CLASS,  # TODO not applicable is case!?
    "length": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "estimated_mass": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "actual_mass": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "qc_start_date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "qc_end_date": Or(CSV_DATE_ISO, CSV_DATE_US),
}

COORD_SCHEMA = {
    "lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    "ssm_lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    "ssm_lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "ssm_x": Or(CSV_EMPTY, CSV_FLOAT),  # TODO ssm are positive floats?
    "ssm_y": Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_x.se": Or(CSV_EMPTY, CSV_FLOAT),
    "ssm_y.se": Or(CSV_EMPTY, CSV_FLOAT),
}

POS_SCHEMA = {
    "x": Or(CSV_EMPTY, CSV_FLOAT),  # TODO check negatives?
    "y": Or(CSV_EMPTY, CSV_FLOAT),  # TODO check negatives?
    "x.se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "y.se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "u": Or(CSV_EMPTY, CSV_FLOAT),
    "v": Or(CSV_EMPTY, CSV_FLOAT),
    "u.se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "v.se": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
}

CTD_SCHEMA = {
    "ref": METADATA_SCHEMA["device_id"],
    "ptt": METADATA_SCHEMA["ptt"],
    "end.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "max.dbar": CSV_POSITIVE_FLOAT,
    "num": CSV_INT,  # TODO apparently a boolean.
    "n.temp": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "n.cond": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "n.sal": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "temp.dbar": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "temp.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "cond.dbar": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "cond.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "sal.dbar": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "sal.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "n.fluoro": Or(CSV_EMPTY, CSV_INT),
    "fluoro.dbar": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "fluoro.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "n.oxy": Or(CSV_EMPTY, CSV_INT),
    "oxy.dbar": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "oxy.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "qc.profile": CSV_INT,  # TODO apparently a boolean.
    "qc.temp": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "qc.sal": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "sal.corrected.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "created": Or(CSV_DATE_ISO, CSV_DATE_US),
    "modified": Or(CSV_DATE_ISO, CSV_DATE_US),
    "n.photo": Or(CSV_EMPTY, CSV_INT),  # TODO
    "photo.dbar": Or(CSV_EMPTY, CSV_LIST_OF_INT),
    "photo.vals": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    **COORD_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

# metadata
DIAG_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "d.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "lq": CSV_INT,
    "lat.x": CSV_LATITUDE,
    "lon.x": CSV_LONGITUDE,
    "alt.lat": CSV_LATITUDE,
    "alt.lon": CSV_LONGITUDE,
    "n.mess": CSV_POSITIVE_INT,
    "n.mess.120": CSV_INT,
    "best.level": CSV_NEGATIVE_INT,
    "pass.dur": CSV_INT,
    "freq": CSV_POSITIVE_FLOAT,
    "v.mask": CSV_INT,
    "alt": CSV_EMPTY,  # TODO
    "est.speed": Or(CSV_EMPTY, CSV_FLOAT),  # TODO check range.
    "km.from.home": Or(CSV_EMPTY, CSV_FLOAT),
    "iq": CSV_INT,
    "nops": CSV_INT,
    "deleted": CSV_EMPTY,  # TODO
    "actual.ptt": CSV_INT,
    "error.radius": CSV_INT,
    "semi.major.axis": CSV_INT,
    "semi.minor.axis": CSV_INT,
    "ellipse.orientation": CSV_INT,
    "hdop": CSV_INT,
    "satellite": str,  # TODO
    "diag.id": CSV_INT,
    "lon.y": Or(CSV_EMPTY, CSV_LONGITUDE),
    "lat.y": Or(CSV_EMPTY, CSV_LATITUDE),
    **POS_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

DIVE_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "cnt": CSV_POSITIVE_INT,
    "de.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "surf.dur": CSV_INT,
    "dive.dur": CSV_INT,
    "max.dep": CSV_POSITIVE_FLOAT,
    **{"d" + str(x): Or(CSV_EMPTY, CSV_POSITIVE_FLOAT) for x in range(1, 5)},  # TODO
    **{"v" + str(x): Or(CSV_EMPTY, CSV_FLOAT) for x in range(1, 6)},
    "travel.r": Or(CSV_EMPTY, CSV_FLOAT),  # TODO
    "homedist": Or(CSV_EMPTY, CSV_FLOAT),  # TODO
    "bottom": Or(CSV_EMPTY, CSV_FLOAT),  # TODO
    **{"t" + str(x): CSV_FLOAT for x in range(1, 5)},  # TODO
    "d.speed": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),  # TODO
    "n.depths": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "n.speeds": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "depth.str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "speed.str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "propn.str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),
    "percent.area": Or(CSV_EMPTY, CSV_FLOAT),
    "residual": CSV_POSITIVE_INT,
    "grp.number": CSV_POSITIVE_INT,
    "d5": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),  # wtf...
    "t5": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "degc.str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),  # TODO
    "illum.str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),  # TODO
    **{
        x: Or(CSV_EMPTY, CSV_POSITIVE_INT)
        for x in [
            "pca.desc",
            "pca.btm",
            "pca.asc",
            "pca.max.desc",
            "pca.max.btm",
            "pca.max.asc",
            "pca.mean.desc",
            "pca.mean.btm",
            "pca.mean.asc",
        ]
    },
    **{
        x: Or(CSV_EMPTY, CSV_POSITIVE_FLOAT)
        for x in ["swim.eff.desc", "swim.eff.btm", "swim.eff.asc", "swim.eff.whole"]
    },
    **{
        x: Or(CSV_EMPTY, CSV_POSITIVE_INT)
        for x in [
            "secs.desc",
            "secs.btm",
            "secs.asc",
            "pitch.desc",
            "pitch.btm",
            "pitch.asc",
        ]
    },
    "pitch.str": Or(CSV_EMPTY, CSV_LIST_OF_FLOAT),  # TODO
    "qc": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    **{"d" + str(x): Or(CSV_EMPTY, CSV_POSITIVE_FLOAT) for x in range(6, 26)},
    **{"t" + str(x): Or(CSV_EMPTY, CSV_POSITIVE_FLOAT) for x in range(6, 26)},
    "ds.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "start.lat": Or(CSV_EMPTY, CSV_LATITUDE),
    "start.lon": Or(CSV_EMPTY, CSV_LONGITUDE),
    **COORD_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

HAULOUT_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "s.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "e.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "haulout.number": CSV_INT,
    "cnt": CSV_POSITIVE_INT,
    "phosi.secs": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "wet.n": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "wet.min": Or(CSV_EMPTY, CSV_FLOAT),
    "wet.max": Or(CSV_EMPTY, CSV_FLOAT),
    "wet.mean": Or(CSV_EMPTY, CSV_FLOAT),
    "wet.sd": Or(CSV_EMPTY, CSV_FLOAT),
    "end.number": CSV_INT,
    **COORD_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

SSMOUTPUTS_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "lon": COORD_SCHEMA["lon"],
    "lat": COORD_SCHEMA["lat"],
    **POS_SCHEMA,
    "cid": METADATA_SCHEMA["sattag_program"],
}

SUMMARY_SCHEMA = {
    "ref": METADATA_SCHEMA["sattag_program"],
    "ptt": METADATA_SCHEMA["ptt"],
    "cnt": CSV_POSITIVE_INT,
    "s.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "e.date": Or(CSV_DATE_ISO, CSV_DATE_US),
    "div.dist": Or(CSV_EMPTY, CSV_FLOAT),  # TODO
    "surf.tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),  # TODO
    "dive.tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),  # TODO
    "haul.tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),  # TODO
    "n.cycles": CSV_INT,
    "av.depth": CSV_FLOAT,
    "max.depth": CSV_FLOAT,
    "cruise.tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "avg.sst": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "avg.speed": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "sd.depth": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "av.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.n.cycles": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.av.depth": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.max.depth": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.avg.speed": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.sd.depth": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.av.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.sd.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.max.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.dive.tm": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "av.surf.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd.surf.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max.surf.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.av.surf.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.sd.surf.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "dp.max.surf.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "pca": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "swim.eff.desc": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "swim.eff.asc": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "swim.eff.whole": Or(CSV_EMPTY, CSV_POSITIVE_FLOAT),
    "secs.desc": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "secs.asc": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "pitch.desc": Or(CSV_EMPTY, CSV_INT),
    "pitch.asc": Or(CSV_EMPTY, CSV_INT),
    "av.haulout.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd.haulout.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max.haulout.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "av.phosi.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "sd.phosi.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "max.phosi.dur": Or(CSV_EMPTY, CSV_POSITIVE_INT),
    "ssm_lon": COORD_SCHEMA["ssm_lon"],
    "ssm_lat": COORD_SCHEMA["ssm_lat"],
    "ssm_x": COORD_SCHEMA["ssm_x"],
    "ssm_y": COORD_SCHEMA["ssm_y"],
    "ssm_x.se": COORD_SCHEMA["ssm_x.se"],
    "ssm_y.se": COORD_SCHEMA["ssm_y.se"],
    "cid": METADATA_SCHEMA["sattag_program"],
}


class AATAMS_SATTAG_QC_DM_SCHEMA(CSVSchema):
    """The AATAMS SATTAG QC DM SCHEMA class."""

    @staticmethod
    def file2schema(file_str):
        """Generate the schema name from the filename.

        Args:
          file_str: filename.

        Returns:
          str: The schema name string.

        """
        return os.path.basename(file_str).split("_")[0]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.manifest_schema = ...
        self.zip_schema = FILENAMES_IN_ZIP_SCHEMA

        self.file_schemas = {
            "metadata": METADATA_SCHEMA,
            "ctd": CTD_SCHEMA,
            "diag": DIAG_SCHEMA,
            "dive": DIVE_SCHEMA,
            "haulout": HAULOUT_SCHEMA,
            "ssmoutputs": SSMOUTPUTS_SCHEMA,
            "summary": SUMMARY_SCHEMA,
        }

        self.same_keys_content = []
        self.cross_content_scope = {
            "cid": "sattag_program",
        }

    def validate_zip_names(self, file_list):
        """Validate the file names.

        Args:
          file_list: a list of file names.

        Returns:
          Any: The result of schema call.

        Raises:
          SchemaError: If the zip files are non-conformant.

        """
        self.report("Validating filename conventions")
        return Schema(self.zip_schema).validate(file_list)

    def validate_headers_only(self, file_list):
        """Validate the headers of a list of csv files.

        Args:
          file_list: a list of csv files.

        Returns:
          Dict[str,Any]: A dictionary with the result of the schema call for every file header.

        Raises:
          SchemaError: if any header is non-conformant.

        """
        headers = {}
        for file in file_list:
            schema_name = self.file2schema(file)
            schema = self.file_schemas[schema_name]
            self.report("Loading headers in %s" % file)
            header = self.load_csv_header(file)
            self.report("Validating headers in %s" % file)
            headers[schema_name] = self.validate_header(header, schema)
        return headers

    def quick_validation(self, file_list):
        """Perform validation only in zip file names and headers.

        Args:
          file_list: a list of csv files.

        Returns:
          None: if all valid

        Raises:
          SchemaError: if zip or headers are non-conformant.

        """
        self.validate_zip_names(file_list)
        self.validate_headers_only(file_list)

    pass

    def extensive_validation(self, file_list):
        """Extensive validation of files within a AATAMS_DM zip.

        1. Filename conventions
        2. Metadata headers
        3. Data rows types
        4. Data rows relationships
        5. Data rows cross relationships with the metadata

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

        self.headers = {}
        self.headers["metadata"], self.metadata = self.validate_file(metadata_file[0])

        if self.cross_content_scope:
            self.report("\tPopulating cross content based on %s" % metadata_file)
            ckeys = self.cross_content_scope.keys()
            self.cross_values = self.compute_cross_values(self.metadata, keys=ckeys)

        for file in file_list:
            schema_name = self.file2schema(file)
            header, valid_data = self.validate_file(file)
            self.headers[schema_name] = header
            setattr(self, schema_name, valid_data)

        pass


pass
