from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, PipelineFileCheckType
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
        if re.match(self.file_extension, '.zip'):
            nc_file = self.file_collection.filter_by_attribute_value('extension', '.nc')
            if len(nc_file) != 1:
                raise InvalidInputFileError(
                    "Expecting one netCDF file in ZIP archive '{zip}'".format(zip=self.file_collection.src_path)
                )

            # first process the NetCDF file to set the destination path for the file collection
            nc = nc_file[0]
            set_nc_dest_path = SoopCo2FileClassifier.dest_path(nc)
            nc.dest_path = os.path.join(set_nc_dest_path, nc.name)
            nc.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            nc.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK

            # SOOP-CO2 DM and FRMAP .txt,.pdf or/and .xml files. Set check type to NONEMPTY and publish type to UPLOAD_ONLY
            non_nc_files = self.file_collection.filter_by_attribute_id('check_type', PipelineFileCheckType.NO_ACTION)
            for non_nc in non_nc_files:
                non_nc.check_type = PipelineFileCheckType.NONEMPTY_CHECK
                non_nc.publish_type = PipelineFilePublishType.UPLOAD_ONLY
                non_nc.dest_path = os.path.join(set_nc_dest_path, non_nc.name)

        elif self.input_file.endswith('dat.txt'):
            # Single text or NetCDF file
            # Realtime files (*dat.txt)
            rt_file = self.file_collection[0]
            nrt_nc_file_path = soop_co2_nrt_nc_generator.process_co2_rt(rt_file)
            rt_file.publish_type = PipelineFilePublishType.ARCHIVE_ONLY
            path_to_archive = SoopCo2FileClassifier.archive_path(rt_file)
            rt_file.archive_path = os.path.join(path_to_archive, rt_file.name)
            nrt_nc_file = PipelineFile(nrt_nc_file_path)
            self.file_collection.add(nrt_nc_file)
            nrt_nc_file.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
            nrt_nc_file.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK
            set_nc_dest_path = SoopCo2FileClassifier.dest_path(nrt_nc_file)
            nrt_nc_file.dest_path = os.path.join(set_nc_dest_path, nrt_nc_file.name)

        elif re.match(self.file_extension, '.nc'):
            # single NetCDF file
            for f in self.file_collection:
                f.publish_type = PipelineFilePublishType.HARVEST_UPLOAD
                f.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK
                nc_dest_path = SoopCo2FileClassifier.dest_path(f)
                f.dest_path = os.path.join(nc_dest_path, f.name)

        else:
            raise InvalidInputFileError(
                "File format '{file}' is invalid should be a SOOP-CO2 realtime file (*dat.txt) \
                or a Delayed mode NetCDF file.".format(file=self.input_file)
            )

    dest_path = SoopCo2FileClassifier.dest_path
