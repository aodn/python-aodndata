import os
import re

import pandas
from aodncore.pipeline import HandlerBase, PipelineFilePublishType, FileType, PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import InvalidInputFileError, PipelineSystemError, InvalidFileContentError

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

    A record of all glider deployment is kept in a .csv file (HarvestListing.csv).
    The deployment status is updated upon recovery and reception of delayed mode data.

    """

    def __init__(self, *args, **kwargs):
        super(AnfogHandler, self).__init__(*args, **kwargs)
        self.allowed_extensions = ['.nc', '.txt', '.zip']
        relative_path_root = os.path.join(self._config.pipeline_config['global']['wip_dir'], 'ANFOG/RT')

        self.resolve_params = {'relative_path_root': relative_path_root}
        self.harvest_mission_file = os.path.join(relative_path_root, AnfogFileClassifier.MISSION_LISTING)

        # store the NC file and the subsequent upload destination calculated from it in the class for other file types
        # to access it when they need to (e.g. dest_path)
        self.primary_nc = None
        self.upload_destination = None

    def preprocess(self):
        """ Preprocessing for RT and DM files.
        Processes ZIP, single NetCDF and single TXT files
        Set destination path based on info in NetCDF files
        Update record of Anfog deployment status('in_progress', 'recovered', 'delayed_mode')
        """

        if self.file_type is FileType.ZIP:
            # First work out whether data in ZIP is Delayed mode or RT
            mode = self.get_data_mode()
            if mode == 'DM':
                self.process_zip_dm()
            elif mode == 'RT':
                self.process_zip_rt()

        elif self.file_type is FileType.NETCDF and re.match(AnfogFileClassifier.DM_REGEX, self.input_file):
            # Single NetCDF file upload only valid for update of DM files
            # => Check for validity done by looking up in mission listing
            # set_mission_status will raise an error if deployment code not in listing
            nc = self.file_collection[0]
            self.set_mission_status(nc.src_path, 'check')
            self.upload_destination = AnfogFileClassifier.get_destination(nc.src_path)
        elif self.input_file.endswith('_status.txt'):
            # handles status file of the form MISSIONID_mission.txt (ex: Yamba20150601_mission.txt)
            # The file act as a trigger for the update of the mission status.
            # Platform cannot be determinate from txt file so set to na=not available
            txt = self.file_collection[0]
            txt.publish_type = PipelineFilePublishType.NO_ACTION
            self.set_mission_status(txt.src_path, 'completed', txt=True)
        else:
            raise InvalidInputFileError("Cannot process a single FV00 file {name}.".
                                        format(name=os.path.basename(self.input_file)))

    def process_zip_common(self, mode):
        if mode == 'RT':
            regex = AnfogFileClassifier.FV00_REGEX
            file_type = 'FV00'
        elif mode == 'DM':
            regex = AnfogFileClassifier.DM_REGEX
            file_type = 'FV00'
        else:
            raise ValueError("invalid mode '{mode}'".format(mode=mode))

        netcdf_collection = self.file_collection.filter_by_attribute_regex('name', regex)
        if len(netcdf_collection) != 1:
            raise InvalidInputFileError("Expecting one {file_type} NetCDF file in ZIP archive '{zip}'".format(
                file_type=file_type, zip=os.path.basename(self.input_file)))

        nc = netcdf_collection[0]
        # use the FV00/01 NetCDF file to set the destination path for other files in the file collection
        self.primary_nc = nc
        self.upload_destination = AnfogFileClassifier.get_destination(nc.src_path)

    def process_zip_dm(self):
        self.process_zip_common('DM')

        # if path exist => update, delete previous DM version;
        #        if not =>  new mission, clear RT data
        results = self.state_query.query_storage(self.upload_destination)
        if results:
            self.logger.info("found previous versions: {results}".format(results=results.keys()))
            self.handle_previous_version('DM', 'update')
        else:
            self.handle_previous_version('DM', 'delayed_mode')
            self.set_mission_status(self.primary_nc.src_path, 'delayed _mode')
            self._set_dm_collection_attributes()

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

        # Check if on S3 mission exist
        # -if yes: need to delete previous netcdf file
        # -if not: add new entry in Harvestmissionfile.csv ;
        results = self.state_query.query_storage(self.upload_destination)
        if results:  # directory exists, contains files that need to be deleted
            self.logger.info("found previous versions: {results}".format(results=results.keys()))
            self.handle_previous_version('RT', 'in_progress')
        else:  # path doesn't exist, mission is new
            self.set_mission_status(self.primary_nc.src_path, 'in_progress')

        # mission transect ancillary files get check_type set to FORMAT_CHECK and publish type to UPLOAD_ONLY
        non_nc_files = PipelineFileCollection(f for f in self.file_collection if f.file_type is not FileType.NETCDF)
        for pf in non_nc_files:
            pf.publish_type = PipelineFilePublishType.UPLOAD_ONLY

    def set_mission_status(self, input_file, message, txt=False):
        """
        load Harvestmission.csv into a data frame
        if new deployment : append row with 'deployment_name, platfom_type, status'
        if update of current deployment: find the relvant data and update the status
        if check : single file submitted, should be an update. Check is to ensure deployment already exist. If not ,
        data should have been submitted with ancillary material(png, pdf...)
        :return: uodated Harvestmission.csv file with new deployment status
        """
        name = os.path.basename(input_file)
        if txt:
            deployment = input_file.split('_')[0]
            platform = 'na'
        else:
            deployment = AnfogFileClassifier.get_deployment_code(input_file)
            platform = AnfogFileClassifier.get_platform(name)

        df = pandas.read_csv(self.harvest_mission_file, names=['deployment_name', 'platform_type', 'status'])

        if df.empty:
            raise PipelineSystemError('Problem loading ANFOG mission listing. Check that file exists/'
                                      'is accessible/ is not empty')

        if message == 'in_progress':  # new deployment
            df.loc[df.index.max() + 1] = [deployment, platform, message]
        elif message == 'check':
            result = df['deployment_name'] == deployment
            if result.any() is False:
                raise InvalidInputFileError(
                    "New delayed mode mission. File should be submitted with ancillary material {deployment}'".format(
                        deployment=deployment)
                )
        elif message == 'delayed_mode' or message == 'completed':
            idx = df['deployment_name'] == deployment
            df['status'][idx] = message

        df.to_csv(self.harvest_mission_file, mode='w', index=False, header=False)

    def handle_previous_version(self, mode, mission_status):
        """
           In RT mode: select previous version of a file that needs to be deleted (.nc and transect pngs)
                       other files are automatically overwritten
           In DM mode either - new DM : delete RT mission files
                            or
                              - update DM : delete previous .nc, other files are automatically overwritten)
         """
        #  RT and DM folder hierarchy similar except that RT has additional level
        #  add REALTIME folder in the destination path
        if mode == 'RT':
            destination = AnfogFileClassifier.make_rt_path(self.upload_destination)
        elif mode == 'DM':
            destination = self.upload_destination
        else:
            raise ValueError("invalid mode '{mode}'".format(mode=mode))

        # set the publishtype set according to file type: netcdf unharvest_delete,
        # everything else (png, txt, kml..) DELETE_ONLY
        previous_file_list = self.state_query.query_storage(destination)

        for filename in previous_file_list.iteritems():
            if filename.endswith('.nc'):
                previous_file = PipelineFile(filename)
                self.file_collection.add(previous_file)
                previous_file.dest_path = os.path.join(destination, previous_file.name)
                previous_file.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
            else:
                if mode == 'RT' and re.match(AnfogFileClassifier.RT_PNG_TRANSECT_REGEX, filename):
                    # delete plot of transect results
                    previous_file = PipelineFile(filename)
                    self.file_collection.add(previous_file)
                    previous_file.dest_path = os.path.join(destination, previous_file.name)
                    previous_file.publish_type = PipelineFilePublishType.DELETE_ONLY
                elif mode == 'DM' and mission_status == 'delayed_mode':
                    # clear all RT files
                    previous_file = PipelineFile(filename)
                    self.file_collection.add(previous_file)
                    previous_file.dest_path = os.path.join(destination, previous_file.name)
                    previous_file.publish_type = PipelineFilePublishType.DELETE_ONLY

    def get_data_mode(self):
        """Based on ZIP content, define the data mode - DM or RT
            - DM : one FV01 + one or more FV00 (ancillary material)
            - RT : one FV00, images (unit???_*.png) and *position_summary.txt
        """
        # Since both DM and RT zip contain FV00 files, first look in zip for .png or position_summary.txt file
        # If present => content is RT material
        # If not => check netcdf file name
        png = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.RT_PNG_REGEX)
        position_txtfile = self.file_collection.filter_by_attribute_regex('name',
                                                                          AnfogFileClassifier.RT_POSITION_SUMMARY)
        if png or position_txtfile:
            return 'RT'
        elif self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.ANFOG_RT_REGEX):
            # Should have matched RT condition in initial test
            raise InvalidFileContentError(
                "Missing some ancillary files(PNGs or summary position file) in ZIP archive {name}".format(
                    name=os.path.basename(self.input_file)))

        elif self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.DM_REGEX):
            return 'DM'
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
        archive_collection = PipelineFileCollection()
        raw = self.file_collection.filter_by_attribute_regex('name', '.*rawfiles.zip$')
        fv00 = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.FV00_REGEX)
        archive_collection.update(raw)
        archive_collection.update(fv00)

        for pf in archive_collection:
            pf.publish_type = PipelineFilePublishType.ARCHIVE_ONLY

        # construct collection of files to upload
        upload_collection = self.file_collection.filter_by_attribute_regex('extension', '^\.(jpg|pdf|kml)$')

        for pf in upload_collection:
            pf.publish_type = PipelineFilePublishType.UPLOAD_ONLY

    def dest_path(self, filepath):
        dest_path = os.path.join(self.upload_destination, os.path.basename(filepath))
        return dest_path

    archive_path = dest_path
