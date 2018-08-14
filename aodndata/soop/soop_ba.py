import os
import re

from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, PipelineFileCheckType, FileType
from aodncore.pipeline import PipelineFileCollection
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileNameError
from aodncore.pipeline import FileClassifier
from ship_callsign import ship_callsign_list

ALLOWED_CONTENT_EXTENSIONS = re.compile(r".*\.(?P<extension>nc|inf|nc\.png|pitch\.csv|roll\.csv|gps\.csv)$")
SHIP_CALLSIGN_LS = ship_callsign_list()


def dest_path(src_file):
    dir_list = []
    fields = FileClassifier._get_file_name_fields(src_file.name)
    ship_code = fields[4]

    if ship_code not in SHIP_CALLSIGN_LS:
        raise InvalidFileNameError(
            "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

    project = fields[0]
    facility = fields[1][:4]
    sub_facility = fields[1]
    platform = "%s_%s" % (ship_code, SHIP_CALLSIGN_LS[ship_code])
    dir_list.extend([project, facility, sub_facility, platform])

    deployment_id = get_deployment_id(src_file, ship_code)

    dir_list.append(deployment_id)
    return FileClassifier._make_path(dir_list)


def archive_path(src_file):
    """Define the archive path based on info from NetCDF"""
    dir_list = []
    fields = FileClassifier._get_file_name_fields(src_file.name)
    ship_code = fields[4]
    if ship_code not in SHIP_CALLSIGN_LS:
        raise InvalidFileNameError(
            "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

    project = fields[0]
    facility = fields[1][:4]
    sub_facility = fields[1]
    raw_folder = 'raw'
    platform = "%s_%s" % (ship_code, SHIP_CALLSIGN_LS[ship_code])
    dir_list.extend([project, facility, sub_facility, raw_folder, platform])

    deployment_id = get_deployment_id(src_file, ship_code)
    dir_list.append(deployment_id)
    return FileClassifier._make_path(dir_list)


def get_deployment_id(src_file, ship_code):
    """
    harmonise way shipcallsign are written in  deployment codes: replace underscore by hyphen
    deployment_id format : shipcallsign_datestart-dateend
    get_nc_att will raise a n exception if the attribute is missing
    :param src_file:
    :param ship_code:
    :return: deployment_id
    """

    deployment_id = FileClassifier._get_nc_att(src_file.src_path, 'deployment_id')
    name_parts = deployment_id.split('_')

    if len(name_parts) >= 3:
        deployment_id = "%s_%s" % (SHIP_CALLSIGN_LS[ship_code], name_parts[-1])

    return deployment_id


class SoopBaHandler(HandlerBase):
    """
    Handler for data from IMOS SOOP BA
    It handles the following file types:
         * ZIP;
         * NetCDF;
    """

    def __init__(self, *args, **kwargs):
        super(SoopBaHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.zip']

    def preprocess(self):
        """ Preprocessing of Zip archive and NetCDF files
            Preprocessing consist in setting the destination path AND deleting previous version files
            - Zip contains netcdf , images ,text, doc, or xml file and raw file to archive
             dest_path is generated based on info stored in FV01 NetCDF file.
             update check_type and publish_type according to destination :
             raw files :  move to archive =>publish_type property to 'archive'
            - text, doc, xml, images: basic checks
              uploaded to S3 => set check_type and publish_type attributesge accordingly
        """

        netcdf = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
        if len(netcdf) != 1:
            raise InvalidInputFileError(
                "Expecting one netCDF file from input file '{infile}'".format(infile=os.path.basename(self.input_file)))

        nc = netcdf[0]
        destination = dest_path(nc)
        nc.dest_path = os.path.join(destination, nc.name)

        results = self.state_query.query_storage(destination)
        files_to_delete = self.get_previous_version(results, destination, nc.name)
        if files_to_delete:
            self.file_collection.update(files_to_delete)

        if self.file_type is FileType.ZIP:
            non_nc_files = PipelineFileCollection(f for f in self.file_collection if f.file_type is not FileType.NETCDF)
            for non_nc in non_nc_files:
                non_nc.check_type = PipelineFileCheckType.FORMAT_CHECK
                if non_nc.extension in ['.ek5', '.out', '.raw']:
                    non_nc.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
                    dest_archive = archive_path(nc)
                    non_nc.archive_path = os.path.join(dest_archive, non_nc.name)
                else:
                    non_nc.publish_type = PipelineFilePublishType.UPLOAD_ONLY
                    non_nc.dest_path = os.path.join(destination, non_nc.name)

                    files_to_delete = self.get_previous_version(results, destination, non_nc.name)
                    if files_to_delete:
                        self.file_collection.update(files_to_delete)

    def get_previous_version(self, previous_file_list, path, input_file_name):
        """
            Find previous version of each incoming file based on its type/extension and
            add them to the filecollection with the correct publish type
            extension can be: .inf', '.nc.png','.pitch.csv','.roll.csv',.gps.csv'
            inputs: previous_file_list : dictionary containing file listing(full path) and metadata from destination
                  input_file :  file basename
                   path : full destination path
        """

        if not previous_file_list:
            return

        files_to_delete = PipelineFileCollection()

        try:
            extension = ALLOWED_CONTENT_EXTENSIONS.match(input_file_name).groupdict()['extension']
        except KeyError:
            raise ValueError("unable to determine extension from file name {infile}".format(infile=input_file_name))

        # get list of previous files basename  to search through
        basenames = {os.path.basename(f) for f in previous_file_list}

        this_extension_pattern = re.compile(r".*\.{ext}$".format(ext=extension))
        if input_file_name not in basenames:
            previous_file = [f for f in previous_file_list if this_extension_pattern.match(f)]

            if extension == 'nc':
                if len(previous_file) != 1:
                    raise ValueError("Expected exactly 1 previous versions of the netcdf file, found {n}. Aborting ".format(
                        n=len(previous_file)))
            else:
                # if uploaded file name has the same name published file => no action, file will be overwritten, otherwise
                # sort file per wildcard and work out which one to delete (
                # check previous file widcard :
                # can be '.inf', '.nc.png','.pitch.csv','.roll.csv',.gps.csv'
                if len(previous_file) > 1:
                    raise ValueError(
                        "Found more than one previous versions of the extension '{ext}'. Aborting".format(
                            ext=extension))
                elif len(previous_file) == 0:
                    return

            prev_file = previous_file[0]
            dest_path = os.path.join(path, os.path.basename(prev_file))
            self.logger.info("adding deletion of previous file '{dest_path}'".format(dest_path=dest_path))

            file_to_delete = PipelineFile(prev_file, is_deletion=True, dest_path=dest_path)

            if extension == 'nc':
                file_to_delete.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
            else:
                file_to_delete.publish_type = PipelineFilePublishType.DELETE_ONLY

            files_to_delete.add(file_to_delete)

        return files_to_delete

    dest_path = dest_path
    archive_path = archive_path
