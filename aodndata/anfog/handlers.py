import os
import re

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile, \
    PipelineFileCheckType
from aodncore.pipeline.exceptions import InvalidInputFileError, MissingFileError, InvalidFileContentError

from aodndata.anfog.classifiers import AnfogFileClassifier


class AnfogHandler(HandlerBase):
    """
    Handling glider files in Near Realtime or Delayed mode;
     Delayed mode files (ANFOG, DSTG, NRL) submitted as zip archive of NetCDF(FV00 and FV01), images(.png/.jpg),
      .txt,.pdf and raw data OR as single FV01 NetCDF files.
     RT files submitted in ZIP archive of FV00 files and images.

    Processing of RT files:
    - FV00: harvested
    - images : uploaded to S3

    Processing of DM files result in:
    - FV01:harvested
    - images, reports and misceleous (.pdf and .txt) :uploaded to S3
    - FV00 and rawfiles.zip : archived
    - RT files deleted from S3

    A record of glider deployments is kept in a .csv file (HarvestListing.csv).
    Status text files trigger update of harvest_listing table in database and action follow depending on the status
    """
    VALID_STATUS = ['in_progress', 'delayed-mode', 'renamed',
                    'RECOVERED', 'ABORTED', 'POTENTIALLY-LOST', 'LOST', 'clear-files']

    def __init__(self, *args, **kwargs):
        super(AnfogHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.txt', '.zip', '.csv']

        # store the NC file and the subsequent upload destination calculated from it in the class for other file types
        # to access it when they need to (e.g. dest_path)
        self.primary_nc = None
        self.upload_destination = None

    def preprocess(self):
        """ Preprocessing for RT and DM files.
        Processes ZIP, single NetCDF and single TXT files
        Set destination path based on info in NetCDF files
        Update ANFOG deployment status record table stored in anforg_rt schema

        Status are set by processing a status text file except for status 'in-progress' set by the pipeline.

        These status text files are either pushed to incoming by POs manually(delayed-mode, renamed), or by facility.
        Difference in letter case reflect the origin of the status file:
        => lower case status files manually pushed in incoming by POs, or set by pipeline
        => uppercase status files uploded by facility
        Status are converted to lowercase and written to the HarvestLising file.

        File requirements:
        1- File name like : PL-Mission_status.txt (PL platform: SG seaglider or SL slocum_glider)
                           For ex:
                           SL-Portland20190218_renamed.txt
                           SL-Portland20190218_RECOVERED.txt

        Note that the message cannot contain undercores otherwise the process fails (see function get_destination)

        2- File must be size > 0 but its content is not relevant.

        Valid status are : 'in-progress' : set by pipeline upon reception of first NRT file of a new NRT deployment.
                                           No further action
                           'delayed-mode' : set py pipeline upon reception of new DM dataset. Triggers
                                           deletion of relevant NRT files from S3
                           'renamed' : uploaded by PO when error in deployment name
                                       (either error in date or deployement name). This status triggers clearing of
                                       relevant NRT files from S3.
                           'RECOVERED' : uploaded by facility within 12-24h of glider recovery. No further action.
                                         No further action
                           'ABORTED' : uploaded by facility after aborting mission and within 12-24h of glider recovery.
                                       No further action
                           'POTENTIALLY-LOST' : uploaded by facility when glider becomes irresponsive for extended
                                                period. No further action
                           'LOST' : uploaded by facility when glider is definitely lost at sea. No further action.
                                   Note however that NRT file of lost glider should ultimately be deleted by PO
                                   within a couple of week after reception of the lost status message using the
                                   'cleanup' status message
                           'cleanup-files' : uploaded by PO. Triggers deletion of relevant NRT files from S3. Used for
                                           cleaning S3 REATLIME folder from deployments that will not be processed in
                                           delayed-mode, for example: mission aborted with no valid data, or lost glider

        """
        input_file_basename = os.path.basename(self.input_file)
        if self.input_file.endswith('.txt'):
            txt = self.file_collection.filter_by_attribute_regex('extension', '.txt')
            txt[0].check_type = PipelineFileCheckType.NO_ACTION
            txt[0].publish_type = PipelineFilePublishType.NO_ACTION
            message = input_file_basename.split('_')[1].strip('.txt')

            if message not in AnfogHandler.VALID_STATUS:
                raise InvalidInputFileError("Invalid status message {m}."
                                            "Message can be either 'delayed-mode', 'renamed', 'RECOVERED'"
                                            "'POTENTIALLY_LOST', 'LOST', 'ABORTED' or 'clear-files'"
                                            .format(m=message))

            self.upload_destination = AnfogFileClassifier.get_destination(self.input_file)

            if message in ['renamed', 'clear-files']:
                self.delete_previous_version('RT', message)

            if message != 'clear-files':
                # the "clear-file"  message is not harvested as it is not relevant to deployment status
                self.set_deployment_status(self.input_file, message)

        elif (self.file_type is FileType.ZIP) or re.match(AnfogFileClassifier.DM_REGEX, input_file_basename):
            mode = self.get_data_mode()

            if self.file_type is FileType.ZIP and mode == 'DM':
                self.process_zip_dm()
            elif self.file_type is FileType.ZIP and mode == 'RT':
                self.process_zip_rt()
            elif re.match(AnfogFileClassifier.DM_REGEX, input_file_basename):
                # In Delayed mode, single NetCDF file upload only valid for updates
                # => Check that deployment exists on S3
                self.primary_nc = self.file_collection[0]
                self.upload_destination = AnfogFileClassifier.get_destination(self.primary_nc.src_path)
                results = self.state_query.query_storage(self.upload_destination)
                if results:
                    self.delete_previous_version('DM', 'update')
                else:
                    raise MissingFileError(
                        "New delayed mode deployment. NetCDF file '{file}' "
                        "should have been submitted with ancillary material"
                        .format(file=os.path.basename(self.primary_nc.src_path)))
        else:
            raise InvalidInputFileError("Cannot process the uploaded file {name}."
                                        .format(name=input_file_basename))

    def process_zip_common(self, mode):
        if mode == 'RT':
            regex = AnfogFileClassifier.ANFOG_RT_REGEX
            file_type = 'FV00'
        elif mode == 'DM':
            regex = AnfogFileClassifier.DM_REGEX
            file_type = 'FV01'
        else:
            raise ValueError("invalid mode '{mode}'".format(mode=mode))

        netcdf_collection = self.file_collection.filter_by_attribute_regex('name', regex)
        if len(netcdf_collection) != 1:
            raise InvalidInputFileError("Expecting one '{file_type}' NetCDF file in ZIP archive '{zip}'".format(
                file_type=file_type, zip=os.path.basename(self.input_file)))

        nc = netcdf_collection[0]
        # use the FV00/01 NetCDF file to set the destination path for the file collection
        self.primary_nc = nc
        self.upload_destination = AnfogFileClassifier.get_destination(nc.src_path)

    def process_zip_dm(self):
        """ Process content of DM zip depending on existence of previous version of deployment or not:
            if path exist => update, delete previous DM version;
            if not =>  new deployment, clear RT data
        """
        self.process_zip_common('DM')

        results = self.state_query.query_storage(self.upload_destination)
        self._set_dm_collection_attributes()
        if results:
            self.logger.info("found previous versions: '{results}'".format(results=list(results)))
            self.delete_previous_version('DM', 'update')
        elif not results and re.match(AnfogFileClassifier.ANFOG_DM_REGEX,
                                      os.path.basename(self.primary_nc.src_path)):
            self.delete_previous_version('DM', 'delayed_mode')

    def process_zip_rt(self):
        """
        Set realtime file destination path based on ANFOG_RT FV00 file attributes
        Check that zip contains a fv00 has already been done
        ZIP typically contains :
            - one FV00 (compulsory)
            - IMAGES (PNGs)
        all files have to be uploaded to S3
        """
        self.process_zip_common('RT')
        # publish type of ancillary files set to UPLOAD_ONLY
        non_nc_files = PipelineFileCollection(f for f in self.file_collection if (f.file_type is not FileType.NETCDF))
        non_nc_files.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)

        # Check if deployment exist on S3
        # -if yes: need to delete previous netcdf file
        # -if not: add new entry in Harvestmissionfile.csv ;
        results = self.state_query.query_storage(self.upload_destination)
        if results:  # directory exists, contains files that need to be deleted
            self.delete_previous_version('RT', 'in_progress')
        else:  # path doesn't exist, deployment is new
            self.set_deployment_status(self.primary_nc.src_path, 'in_progress')

    def set_deployment_status(self, input_file, message):
        """
        Write message to Harvestmission.csv file. ingested in RT pieline
        Update the anfog_rt.harvest_listing table after ingestion of csv file by RT pipeline
        Note that to be consistent with the available message in the production DB,
        dashes need to be replaced by underscore, for ex delayed-mode =>delayed_mode
        :return:  Harvestmission.csv updated with deployment specific status
        """
        name = os.path.basename(input_file)
        deployment = AnfogFileClassifier.get_deployment_code(input_file)
        platform = AnfogFileClassifier.get_platform(name)

        listing_path = os.path.join(self.products_dir, AnfogFileClassifier.MISSION_LISTING)
        with open(listing_path, 'w') as f:
            f.write('deployment_name, platform_type, status' + os.linesep)
            row = "%s,%s,%s" % (deployment, platform, message.replace('-', '_').lower())
            f.write(row)

        product = PipelineFile(listing_path)
        product.publish_type = PipelineFilePublishType.HARVEST_ONLY
        product.check_type = PipelineFileCheckType.FORMAT_CHECK
        product.dest_path = os.path.join(self.upload_destination, os.path.basename(listing_path))
        self.file_collection.add(product)

    def delete_previous_version(self, mode, deployment_status):
        """
           In RT mode: 2 cases 1) update of deployment in progress :select previous version of a file that needs to be
                       deleted (.nc)  other files are automatically overwritten
                               2) cleaning RT folder :status "renamed","clear-files"

           In DM mode either - new DM (deployment_status = delayed_mode): delete RT deployment files
                            or
                            - update DM (deployment_status = update):: delete previous .nc,
                            other files are automatically overwritten)
         """

        if mode == 'DM' and deployment_status == 'delayed_mode':
            #  RT and DM folder hierarchy similar except that RT has additional level /REALTIME/
            destination = AnfogFileClassifier.make_rt_path(self.upload_destination)
            delete_file_regex = '%s|%s|%s' % (AnfogFileClassifier.ANFOG_RT_REGEX,
                                              AnfogFileClassifier.RT_PNG_REGEX,
                                              AnfogFileClassifier.RT_POSITION_SUMMARY)
        elif mode == 'DM' and deployment_status == 'update':
            destination = self.upload_destination
            delete_file_regex = AnfogFileClassifier.ANFOG_DM_REGEX
        elif mode == 'RT' and deployment_status in ['renamed', 'clear-files']:
            destination = self.upload_destination
            delete_file_regex = '%s|%s|%s' % (AnfogFileClassifier.ANFOG_RT_REGEX,
                                              AnfogFileClassifier.RT_PNG_REGEX,
                                              AnfogFileClassifier.RT_POSITION_SUMMARY)
        elif mode == 'RT' and deployment_status == 'in_progress':
            destination = self.upload_destination
            delete_file_regex = AnfogFileClassifier.ANFOG_RT_REGEX

        else:
            raise ValueError(
                "Invalid combination of mode '{mode}' and status'{st}'".format(mode=mode, st=deployment_status))

        # publish_type set according to file type: netcdf unharvest_delete,
        # everything else (png, txt, kml..) DELETE_ONLY
        previous_file_list = self.state_query.query_storage(destination).keys()
        self.logger.info("Mode '{mode}' and Status '{status}'".format(mode=mode, status=deployment_status))

        for filename in previous_file_list:
            previous_file = PipelineFile(filename, is_deletion=True, dest_path=destination)
            previous_file.dest_path = os.path.join(destination, previous_file.name)
            # set default publish type to delete only
            previous_file.publish_type = PipelineFilePublishType.DELETE_ONLY
            if previous_file.file_type is FileType.NETCDF:
                previous_file.publish_type = PipelineFilePublishType.DELETE_UNHARVEST

            if re.match(delete_file_regex, previous_file.name):
                self.file_collection.add(previous_file)

                if deployment_status not in ['renamed', 'clear-files'] and re.match(previous_file.name,
                                                               os.path.basename(self.primary_nc.src_path)):
                    # removing file as it will be overwritten. Note that test is invalid in 'renamed' status
                    #  cause primary_nc not set(irrelevant)
                    self.file_collection.discard(previous_file)
                else:
                    self.logger.info(
                        "adding deletion of previous file '{dest_path}'".format(dest_path=previous_file.dest_path))

    def get_data_mode(self):
        """
            1) Set data mode based on NetCDF product type
            If FV01 => DM
            If FV00 is ANFOG_RT =>  RT, then also check zip contain ancillary files,
            (.png or position_summary.txt file)
            If not present => missing RT material
            2) Set format_check type specific to product type(FV00/01) and origin(ANFOG, DSTG or NRL)
        """
        fv01 = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.DM_REGEX)
        adapter_dstg = '%s|%s' % (AnfogFileClassifier.ADAPTER_REGEX, AnfogFileClassifier.DSTG_REGEX)
        anfog_rt = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.ANFOG_RT_REGEX)

        if fv01:
            if re.match(adapter_dstg, fv01[0].name):
                # Adapter and DSTG file not cf and imos compliant
                fv01[0].check_type = PipelineFileCheckType.FORMAT_CHECK

            return 'DM'
        elif anfog_rt:
            # RT file not compliant
            anfog_rt[0].check_type = PipelineFileCheckType.FORMAT_CHECK
            png = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.RT_PNG_REGEX)
            if png:
                return "RT"
            else:
                raise InvalidFileContentError(
                    "Missing ancillary files(PNGs or summary position file) in ZIP archive {name}".format(
                        name=os.path.basename(self.input_file)))
        else:
            raise InvalidInputFileError(
                "Expecting one NetCDF file in ZIP archive '{zip}'".format(
                    zip=os.path.basename(self.input_file))
            )

    def _set_dm_collection_attributes(self):
        # ZIP usually contains different type of files to be archive or published:
        # FV00 and rawfiles.zip -> archive
        # jpg,kml and QC_Report.pdf -> S3

        # construct collection of files to archive
        raw = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.RAW_FILES_REGEX)
        # necessary to  specify the format check for the FV00 file cause they fail the netcdf compliance checks
        raw.set_check_types(PipelineFileCheckType.FORMAT_CHECK)
        raw.set_publish_types(PipelineFilePublishType.ARCHIVE_ONLY)

        # construct collection of files to upload
        upload_to_s3 = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.UPLOAD_TO_S3_REGEX)
        upload_to_s3.set_publish_types(PipelineFilePublishType.UPLOAD_ONLY)


    def dest_path(self, filepath):
        dest_path = os.path.join(self.upload_destination, os.path.basename(filepath))
        return dest_path


archive_path = AnfogHandler.dest_path
