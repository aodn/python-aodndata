from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, PipelineFileCheckType, FileType
from aodncore.pipeline import PipelineFileCollection
from aodncore.pipeline.exceptions import InvalidInputFileError
import soop_co2_nrt_nc_generator
from soop_co2_classifier import SoopCo2FileClassifier
import re
import os

class SoopCo2Handler(HandlerBase):
    """
    Handler for data from IMOS SOOP CO2(DM, RT) and Future Reef Map Project.
    It handles the following file types:
         * ZIP;
         * NetCDF;
         * TXT;
    """

    def __init__(self, *args, **kwargs):
        super(SoopCo2Handler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.txt', '.zip']

    def preprocess(self):
        """ Preprocessing for NRT and DM files
           - NRT: generate a NetCDF files based on input text file.
             Set the input file publish_type property to 'archive'
           - DM file collection: update the check_type and publish_type properties for non-NetCDF files.
             These files are not checked or harvested, but uploaded to S3

        """
        # Delayed mode file submitted as a zip archive
        if self.file_extension == '.zip':
            nc_file = self.file_collection.filter_by_attribute_id('file_type', FileType.NETCDF)
            if len(nc_file) != 1:
                raise InvalidInputFileError(
                    "Expecting one netCDF file in ZIP archive '{zip}'".format(zip=os.path.basename(self.input_file))
                )

            # first process the NetCDF file to set the destination path for the file collection
            nc = nc_file[0]
            set_nc_dest_path = SoopCo2FileClassifier.dest_path(nc)
            nc.dest_path = os.path.join(set_nc_dest_path, nc.name)


            # SOOP-CO2 DM and FRMAP .txt,.pdf or/and .xml files. Set check type to NONEMPTY and publish type to UPLOAD_ONLY
            non_nc_files = PipelineFileCollection(f for f in self.file_collection if f.file_type is not FileType.NETCDF)
            for non_nc in non_nc_files:
                non_nc.check_type = PipelineFileCheckType.FORMAT_CHECK
                non_nc.publish_type = PipelineFilePublishType.UPLOAD_ONLY
                non_nc.dest_path = os.path.join(set_nc_dest_path, non_nc.name)

        elif self.input_file.endswith('dat.txt'):
            # Single text file
            # Realtime files (*dat.txt)
            rt_file = self.file_collection[0]
            rt_file.publish_type = PipelineFilePublishType.ARCHIVE_ONLY

            nrt_nc_file_path = soop_co2_nrt_nc_generator.process_co2_rt(rt_file, self.products_dir)
            nrt_nc_file = PipelineFile(nrt_nc_file_path)
            self.file_collection.add(nrt_nc_file)
            nrt_nc_file.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK
            nrt_nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            set_nc_dest_path = SoopCo2FileClassifier.dest_path(nrt_nc_file)
            nrt_nc_file.dest_path = os.path.join(set_nc_dest_path, nrt_nc_file.name)
            print "File cooll %s" % self.file_collection[1]

        elif self.file_type is FileType.NETCDF:
            # single NetCDF file
            nc = self.file_collection[0]
            nc_dest_path = SoopCo2FileClassifier.dest_path(nc)
            nc.dest_path = os.path.join(nc_dest_path, nc.name)

        else:
            raise InvalidInputFileError(
                "File format '{file}' is invalid. Should be a SOOP-CO2 realtime file (*dat.txt) " 
                "or a Delayed Mode zip archive or NetCDF file.".format(file=self.input_file)
            )

    dest_path = SoopCo2FileClassifier.dest_path
    archive_path = SoopCo2FileClassifier.archive_path