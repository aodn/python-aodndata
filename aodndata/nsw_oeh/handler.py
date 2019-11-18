from __future__ import print_function

import os
import re
import shutil
import zipfile
from collections import OrderedDict
from datetime import datetime

import fiona
from aodncore.pipeline.exceptions import InvalidFileContentError
from aodncore.pipeline import HandlerBase, FileType, PipelineFilePublishType
from fiona.errors import FionaValueError

ACCEPTED_CRS = ('W84Z55', 'W84Z56')
ACCEPTED_PROJ4 = ({'init': 'epsg:32756'}, {'init': 'epsg:32755'})
VERTICAL_CRS = dict(BTY='AHD', BKS='GRY')
SHAPEFILE_EXTENSIONS = ('CPG', 'cpg', 'dbf', 'prj', 'sbn', 'sbx', 'shp', 'shp.xml', 'shx')
SHAPEFILE_ATTRIBUTES = {'MB': {'SDate', 'Location', 'Area', 'XYZ_File', 'XYA_File', 'MAX_RES', 'Comment'},
                        'STAX': {'SDate', 'Location', 'Source_xyz', 'AREA', 'est_no'}
                        }
SHAPEFILE_PATTERN = '.*_SHP.(' + '|'.join(SHAPEFILE_EXTENSIONS) + ')' #re.compile('.*_SHP.(' + '|'.join(SHAPEFILE_EXTENSIONS) + ')')
ALL_EXTENSIONS = ('zip', 'xyz', 'xya', 'tif', 'tiff', 'sd', 'kmz', 'pdf') + SHAPEFILE_EXTENSIONS
SOFTWARE_CODES = ('FLD', 'FMG', 'ARC', 'GTX', 'GSP', 'HYP', 'QIM')
SOFTWARE_PATTERN = '(' + '|'.join(SOFTWARE_CODES) + ')(\d{3})$'
FILE_VERSIONS = ('FV00', 'FV01', 'FV02')
SURVEY_NAME_PATTERN = re.compile('NSWOEH_(\d{8}_[A-Za-z]+)')
SURVEY_METHODS = {'MB': 'Multi-beam', 'STAX': 'Single-beam', 'LD': 'LIDAR-LADS'}
SURVEY_METHODS_PATTERN = re.compile('NSWOEH_[^_]+_[^_]+_(' + '|'.join(SURVEY_METHODS.keys()) + ')')
SYSTEM_TYPES = 'GSS|R2S|MRG'
SYSTEM_TYPES_PATTERN = re.compile(r"(BTY|BKS)GRD\d{3}" + "({})".format(SYSTEM_TYPES))

# Methods that only require a coverage shapefile, nothing else is checked, just stored as is in the original zip
BASIC_PACKAGED_METHODS = ('STAX', 'LD')


def is_date(field):
    """Return true if field is a valid date in the format YYYYMMDD, false otherwise."""
    try:
        datetime.strptime(field, '%Y%m%d')
    except ValueError:
        return False

    return len(field) == 8


def check_crs(crs_field):
    """
    Check the coordinate reference system specified in the given
    field within a file name. Return an empty list or a list with
    a single message.
    """
    message = []
    if crs_field not in ACCEPTED_CRS:
        message.append("Coordinate system should be one of {}.".format(ACCEPTED_CRS))
    return message


def get_name_fields(path):
    """
    Return a tuple consisting of
    1) a list of underscore-separated fields in the file name, and
    2) the file name extension (part of name after the first '.')
    """
    file_name = os.path.basename(path)
    name_ext = file_name.split('.', 1)
    fields = name_ext[0].split('_')
    extension = name_ext[1] if len(name_ext) > 1 else ''
    return fields, extension


def get_survey_name(path):
    """
    Return the survey name (date and location) from the file name,
    or an empty string if file name is incorrect.
    """
    file_name = os.path.basename(path)
    m = SURVEY_NAME_PATTERN.match(file_name)
    if m:
        return m.groups()[0]
    else:
        return ''


def get_survey_methods(path):
    """
    Return the survey methods code from the file name,
    or an empty string if file name is incorrect.
    """
    file_name = os.path.basename(path)
    m = SURVEY_METHODS_PATTERN.match(file_name)
    if m:
        return m.groups()[0]
    else:
        return ''


class NSWOEHSurveyProcesor:
    def __init__(self, zip_file):
        self.zip_file = zip_file
        self.survey_name = get_survey_name(zip_file)
        try:
            self.survey_date, self.survey_location = self.survey_name.split('_')
        except ValueError:
            self.survey_date = None
            self.survey_location = None
        self.survey_methods = get_survey_methods(zip_file)
        self.zip_contents = []

    def check_name_basic(self, file_name):
        """
        Check file_name against the basic NSW OEH naming convention (first 4 fields). If the name does not meet the
        conventions, a list of messages detailing the errors is returned. An empty list indicates perfect compliance.
        """
        messages = []

        # check for space characters
        if ' ' in file_name:
            messages.append("File name should not contain spaces")

        fields, extension = get_name_fields(file_name)
        if len(fields) < 4:
            messages.append("File name should have at least 4 underscore-separated fields.")

        # check organisation (NSWOEH) field
        if len(fields) == 0:
            return messages
        if fields[0] != 'NSWOEH':
            messages.append("File name must start with 'NSWOEH'")

        # check date field
        if len(fields) <= 1:
            return messages
        if not is_date(fields[1]):
            messages.append("Field 2 should be a valid date (YYYYMMDD).")
        elif self.survey_date and fields[1] != self.survey_date:
            messages.append(
                "Wrong survey date {f} (zip file name has {z})".format(f=fields[1], z=self.survey_date)
            )

        # check survey location field
        if len(fields) <= 2:
            return messages
        if not re.match("[A-Za-z]+$", fields[2]):
            messages.append("Field 3 should be a location code consisting only of letters.")
        elif self.survey_location and fields[2] != self.survey_location:
            messages.append(
                "Wrong location {f} (zip file name has {z})".format(f=fields[2], z=self.survey_location)
            )

        # check survey methods field
        if len(fields) <= 3:
            return messages
        if fields[3] not in SURVEY_METHODS:
            messages.append("Field 4 should be a valid survey method code")
        elif self.survey_methods and fields[3] != self.survey_methods:
            messages.append(
                'Wrong survey method code {f}, expected {z}'.format(f=fields[3], z=self.survey_methods)
            )

        return messages

    def check_name(self, file_name):
        """
        Check file_name against the full NSW OEH naming convention. If the name
        does not meet the conventions, a list of messages detailing the
        errors is returned. An empty list indicates perfect compliance.
        """
        messages = self.check_name_basic(file_name)

        fields, extension = get_name_fields(file_name)

        # only 4 fields required for zip file and "basic packaged" files
        if extension == 'zip' or self.survey_methods in BASIC_PACKAGED_METHODS:
            return messages

        if extension not in ALL_EXTENSIONS:
            messages.append("Unknown extension '{}'".format(extension))

        # check the product type and details field
        if len(fields) < 5:
            messages.append("File name should have at least 5 underscore-separated fields.")
            return messages

        # Determine file type from 5th field
        m = re.match("BTY|BKS|SHP$|ScientificRigour$", fields[4])
        if not m:
            messages.append("Unknown product type '{}'".format(fields[4]))
            return messages

        product_type = m.group()

        # Metadata document (PDF)
        if product_type == "ScientificRigour":
            if extension != "pdf":
                messages.append("The Scientific Rigour (metadata) sheet must be in PDF format.")
            return messages

        # Coverage shapefile
        if product_type == "SHP":
            if extension not in SHAPEFILE_EXTENSIONS:
                messages.append("Unknown extension for shapefile '{}'".format(extension))
            return messages

        # KMZ file, no additional details needed
        if product_type in ('BKS', 'BTY') and extension == 'kmz':
            return messages

        # Bathymetry or backscatter data file
        if len(fields) < 9:
            messages.append(
                "Bathymetry & backscatter file names should have at least 9 underscore-separated fields."
            )

        if not SYSTEM_TYPES_PATTERN.match(fields[4]):
            messages.append(
                "Field 5 contains unknown data product details " +
                "(expecting 'GRD', grid resolution in metres, system type {}).".format(SYSTEM_TYPES)
            )

        if len(fields) < 6:
            return messages
        messages.extend(check_crs(fields[5][:6]))
        hhh = VERTICAL_CRS[product_type]
        if fields[5][6:] != hhh:
            messages.append(
                "For a '{}' product, field 6 should end with '{}'.".format(product_type, hhh)
            )

        # check 7th field (software and version)
        if len(fields) < 7:
            return messages
        if not re.match(SOFTWARE_PATTERN, fields[6]):
            messages.append(
                "Field 7 should be a valid software code {} "
                "followed by a 3-digit version number.".format(SOFTWARE_CODES)
            )

        # check 8th field (product export date)
        if len(fields) < 8:
            return messages
        if not is_date(fields[7]):
            messages.append("Field 8 should be a valid date (YYYYMMDD).")

        # check 9th field file version
        if len(fields) < 9:
            return messages
        if fields[8] not in FILE_VERSIONS:
            messages.append("Field 9 should be a file version number {}".format(FILE_VERSIONS))

        return messages

    def check_shapefile(self, shapefile_path):
        """
        Check that the shapefile (inside the zip) has
         * only one feature;
         * the expected attributes;
         * one of two accepted projections;
        :param str shapefile_path: full path of shapefile inside zip (start with '/')
        :return: List of error messages (empty if none).
        :rtype: list
        """

        messages = []

        try:
            f = fiona.open(shapefile_path, vfs='zip://' + self.zip_file)
        except (IOError, FionaValueError) as e:
            messages.append("Unable to open shapefile ({err})".format(err=e))
            return messages

        # number of features
        if len(f) != 1:
            messages.append("Shapefile should have exactly one feature (found {})".format(len(f)))

        # attributes
        required_att = SHAPEFILE_ATTRIBUTES.get(self.survey_methods, set())
        missing_att = required_att - set(f.schema['properties'].keys())
        if missing_att:
            messages.append("Missing required attributes {}".format(list(missing_att)))

        # projection
        if f.crs not in ACCEPTED_PROJ4:
            messages.append(
                "Unknown CRS {}, expected {} or {}".format(f.crs, *ACCEPTED_PROJ4)
            )

        # check that survey date match what's in the file name
        fields, _ = get_name_fields(shapefile_path)
        rec = next(iter(f))
        sdate = rec['properties'].get('SDate')
        if sdate and sdate != fields[1]:
            messages.append(
                "Date in shapefile field SDate ({sdate}) inconsistent with file name date ({fdate})".format(
                    sdate=sdate, fdate=fields[1]
                )
            )

        f.close()
        return messages

    def check_all(self):
        """
        Check the contents of the zip file for consistency, presence of required files
        and compliance with conventions.
        :return: error messages organised by heading
        :rtype: OrderedDict
        """
        # dict to contain all error messages
        report = OrderedDict()

        # check zip file name
        messages = self.check_name_basic(self.zip_file)
        if messages:
            report[self.zip_file] = messages

        # open zip file and read content list
        if not zipfile.is_zipfile(self.zip_file):
            report[self.zip_file] = ["Not a valid zip archive!"]
            return report
        with zipfile.ZipFile(self.zip_file) as zf:
            path_list = zf.namelist()

        # Check each individual file name
        have_metadata = False
        have_coverage = False
        have_xyz = False
        for file_path in sorted(path_list):
            file_name = os.path.basename(file_path)
            if not file_name:
                continue  # skip directories

            messages = self.check_name(file_name)

            if file_name.endswith('ScientificRigour.pdf'):
                have_metadata = True

            if file_name.endswith('.xyz'):
                have_xyz = True

            # Check coverage shapefile
            if file_name.endswith('_SHP.shp'):
                have_coverage = True
                messages.extend(self.check_shapefile('/' + file_path))

            if messages:
                report[file_name] = messages
            else:
                self.zip_contents.append(file_path)

        # Overall checks...
        messages = []

        # metadata sheet (PDF) exists
        if not have_metadata:
            messages.append("Missing metadata file (PDF format)")

        # shapefile exists
        # TODO: Check there is exactly one coverage shapefile
        if not have_coverage:
            messages.append("Missing survey coverage shapefile")

        # at least one XYZ file for MB surveys
        if not have_xyz and self.survey_methods == 'MB':
            messages.append("Missing bathymetry xyz file")

        if messages:
            report["Zip file contents"] = messages

        return report

    def get_dest_path(self):
        """
        Return the relative path where the contents of the zip file should be
        published to on S3. Raise an exception if required metadata are missing.
        :return: relative path
        :rtype: str
        """
        survey_year = self.survey_name[:4]
        methods_name = SURVEY_METHODS.get(self.survey_methods, '')
        if not methods_name or not survey_year or not self.survey_name:
            raise ValueError(
                "Could not determine destination path for {zip}".format(zip=self.zip_file)
            )
        return os.path.join('NSW-OEH', methods_name, survey_year, self.survey_name)

class NswOehHandler(HandlerBase):
    def __init__(self, *args, **kwargs):
        super(NswOehHandler, self).__init__(*args, **kwargs)

        self.allowed_extensions = ['.zip']
        self.survey_path = None

    def preprocess(self):
        self.file_collection.add(self.input_file_object)
        self.input_file_object.publish_type = PipelineFilePublishType.HARVEST_UPLOAD

        pz = NSWOEHSurveyProcesor(self.input_file)
        report = pz.check_all()

        if len(report) > 0:
            raise_string = ''
            for heading, messages in report.items():
                raise_string += "\n{heading}:\n{messages}\n".format(
                    heading=heading,
                    messages="\n".join(["{0}. {1}".format(i+1, messages) for i, messages in enumerate(messages)]))

            raise InvalidFileContentError(
                "Could not determine data category for '{name}'\n{raise_string}".format(
                    name=os.path.basename(self.input_file),
                    raise_string=raise_string))

        # stax files
        if pz.survey_methods in BASIC_PACKAGED_METHODS:
            self.file_collection.set_publish_types(PipelineFilePublishType.NO_ACTION)  # reset all publish types

            self.file_collection.filter_by_attribute_id('file_type', FileType.ZIP).\
                set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)  # publish zip file

            self.file_collection.filter_by_attribute_regex('name', SHAPEFILE_PATTERN).set_publish_types(
                PipelineFilePublishType.HARVEST_UPLOAD)  # publish files matching pattern


        self.survey_path = pz.get_dest_path()

    def dest_path(self, filepath):
        return os.path.join(self.survey_path, os.path.basename(filepath))
