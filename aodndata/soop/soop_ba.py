import os
import re

from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, PipelineFileCheckType, FileType
from aodncore.pipeline import PipelineFileCollection
from aodncore.pipeline.exceptions import InvalidInputFileError

from aodndata.soop.soop_ba_classifier import SoopBaFileClassifier


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
        if self.file_type is FileType.ZIP:
            netcdf = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
            # if uploaded file is ZIP check that ZIP contains a NetCDF
            if len(netcdf) != 1:
                raise InvalidInputFileError(
                    "Expecting one netCDF file in ZIP archive '{zip}'".format(zip=os.path.basename(self.input_file))
                )

            # first process the NetCDF file to set the destination path for the file collection.
            nc = netcdf[0]
            nc.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK
            destination = SoopBaFileClassifier.dest_path(nc)
            nc.dest_path = os.path.join(destination, nc.name)

            # based on file type/extension,  add  previous verions of files to filecollection with attribute DELETE
            # netcdf file have to be deleted since filename contains creation date=>never overwritten
            results = self.state_query.query_storage(destination)
            if results:
                self.get_previous_version(results, destination, nc.name)

            non_nc_files = PipelineFileCollection(f for f in self.file_collection if f.file_type is not FileType.NETCDF)
            for non_nc in non_nc_files:
                non_nc.check_type = PipelineFileCheckType.FORMAT_CHECK
                if non_nc.extension in ['.ek5', '.out', '.raw']:
                    non_nc.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
                    dest_archive = SoopBaFileClassifier.archive_path(nc)
                    non_nc.archive_path = os.path.join(dest_archive, non_nc.name)
                else:
                    non_nc.publish_type = PipelineFilePublishType.UPLOAD_ONLY
                    non_nc.dest_path = os.path.join(destination, non_nc.name)
                    if results:
                        self.get_previous_version(results, destination, non_nc.name)

        else:  # singe netcdf file
            netcdf = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
            nc = netcdf[0]
            nc.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK
            destination = SoopBaFileClassifier.dest_path(nc)
            nc.dest_path = os.path.join(destination, nc.name)

            # add  previous verions of netcdf file to filecollection with attribute DELETE
            # netcdf file have to be deleted since filename contains creation date=>never overwritten
            results = self.state_query.query_storage(destination)
            if results:
                self.get_previous_version(results, destination, nc.name)

    def get_previous_version(self, previous_file_list, path, input_file_name):
        """
            Find previous version of each incoming file based on its type/extension and
            add them to the filecollection with the correct publish type
            extension can be: .inf', '.nc.png','.pitch.csv','.roll.csv',.gps.csv'
            inputs: previous_file_list : dictionary containing file listing(full path) and metadata from destination
                  input_file :  file basename
                   path : full destination path
        """
        if input_file_name.endswith('.nc'):
            r = re.compile(".*.nc$")
            prev_file = filter(r.match, previous_file_list.keys())
            assert len(prev_file) == 1, "Found more than one previous versions of the netcdf file. Aborting "
            self.add_previous_version_file_to_collection(prev_file[0], path, PipelineFilePublishType.DELETE_UNHARVEST)
        else:
            # Either the uploded file name has the same name published file => no action, file will be overwritten
            # OR Sort file per wildcard and work out which one to delete (
            # check previous file widcard :
            # can be '.inf', '.nc.png','.pitch.csv','.roll.csv',.gps.csv'
            if input_file_name in previous_file_list.keys():
                pass
            else:
                previous_version_extension = input_file_name.split('.')[1:]
                p = previous_version_extension
                if len(p) > 1:
                    extension = "%s%s%s%s%s" % ('.*.', p[0], '.', p[1], '$')
                else:
                    extension = "%s%s%s" % ('.*.', p[0], '$')

                r = re.compile(extension)
                prev_file = filter(r.match, previous_file_list.keys())

                assert len(
                    prev_file) <= 1, 'Found more than one previous versions of the extension %s. Aborting' % extension
                if len(prev_file) == 1:
                    self.add_previous_version_file_to_collection(prev_file[0], path,
                                                                 PipelineFilePublishType.DELETE_ONLY)

    def add_previous_version_file_to_collection(self, prev_file, path, publish_type):
        """add a previous  version file to the a file collection with the relevant attributes"""
        file_to_delete = PipelineFile(prev_file, is_deletion=True)
        self.file_collection.add(file_to_delete)
        file_to_delete.dest_path = os.path.join(path, os.path.basename(prev_file))
        file_to_delete.publish_type = publish_type

    dest_path = SoopBaFileClassifier.dest_path
    archive_path = SoopBaFileClassifier.archive_path
