import os
import re
import pandas

from aodncore.pipeline import HandlerBase, PipelineFilePublishType, PipelineFileCheckType, FileType, \
    PipelineFileCollection, PipelineFile
from aodncore.pipeline.exceptions import InvalidInputFileError, PipelineSystemError
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

    def preprocess(self):
        """ Preprocessing for RT and DM files.
        Processes ZIP, single NetCDF and single TXT files
        Set destination path based on info in NetCDF files
        Update record of Anfog deployment status('in_progress', 'recovered', 'delayed_mode')
        """

        if self.file_type is FileType.ZIP:
            # First work out whether data in ZIP is Delayed mode or RT
            mode = AnfogFileClassifier.set_data_mode(self)
            if mode is None:
                raise InvalidInputFileError("Could not work out the data mode (DM, RT) from Zip content {name}.".
                                            format(name=os.path.basename(self.input_file)))
            elif mode == 'DM':
                self.process_zip_dm()
            else:
                self.process_zip_rt()

        elif self.file_type is FileType.NETCDF and re.match(AnfogFileClassifier.DM_REGEX, self.input_file):
            # Single NetCDF file upload only valid for update of DM files
            # => Check for validity done by looking up in mission listing
            # set_mission_status will raise an error if deployment code not in listing
            nc = self.file_collection[0]
            deployment = AnfogFileClassifier.get_deployment_code(nc)
            platform = AnfogFileClassifier.get_platform(nc.name)
            self.set_mission_status(deployment, platform, 'check')
            nc_dest_path = AnfogFileClassifier.dest_path(nc, 'DM')
            nc.dest_path = os.path.join(nc_dest_path, nc.name)
        elif self.input_file.endswith('_status.txt'):
            # handles status file of the form MISSIONID_mission.txt (ex: Yamba20150601_mission.txt)
            # The file act as a trigger for the update of the mission status.
            # Platform cannot be determinate from txt file so set to na=not available
            txt = self.file_collection[0]
            txt.publish_type = PipelineFilePublishType.NO_ACTION
            deployment = txt.name.split('_')[0]
            self.set_mission_status(deployment, 'na', 'completed')
        else:
            raise InvalidInputFileError("Cannot process a single FV00 file {name}.".
                                        format(name=os.path.basename(self.input_file)))

    def process_zip_dm(self):
        is_dm_netcdf = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.DM_REGEX)
        if len(is_dm_netcdf) != 1:
            raise InvalidInputFileError(
                "Expecting one FV01 NetCDF file in ZIP archive '{zip}'".format(
                    zip=os.path.basename(self.input_file))
            )
        else:
            fv01 = is_dm_netcdf[0]
            # first process the FV01 NetCDF file to set the destination path for the file collection
            destination = AnfogFileClassifier.dest_path(fv01, 'DM')
            fv01.dest_path = os.path.join(destination, fv01.name)
            fv01.check_type = PipelineFileCheckType.NC_COMPLIANCE_CHECK

            # if path exist => update, delete previous DM version;
            #        if not =>  new mission, clear RT data
            results = self.state_query.query_storage(destination)
            if results:
                self.handle_previous_version('DM', destination, 'update')
            else:
                path_to_rt_folder = AnfogFileClassifier.dest_path(fv01, 'RT')
                self.handle_previous_version('DM', path_to_rt_folder, 'delayed_mode')
                deployment = AnfogFileClassifier.get_deployment_code(fv01)
                platform = AnfogFileClassifier.get_platform(fv01.name)
                self.set_mission_status(deployment, platform, 'delayed _mode')

            # ZIP usually contains different type of files to be archive or published:
            # FV00 and rawfiles.zip -> archive
            # jpg,kml and QC_Report.pdf -> S3
            # TODO revisit set_attribute  implement in collection classmethod
            raw = self.file_collection.filter_by_attribute_regex('name', '.*rawfiles.zip$')
            AnfogFileClassifier.set_attributes_per_file_type(raw, 'archive', destination)
            fv00 = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.FV00_REGEX)
            AnfogFileClassifier.set_attributes_per_file_type(fv00, 'archive', destination)
            jpg = self.file_collection.filter_by_attribute_value('extension', '.jpg')
            AnfogFileClassifier.set_attributes_per_file_type(jpg, 'S3upload', destination)
            pdf = self.file_collection.filter_by_attribute_value('extension', '.pdf')
            AnfogFileClassifier.set_attributes_per_file_type(pdf, 'S3upload', destination)
            kml = self.file_collection.filter_by_attribute_value('extension', '.kml')
            AnfogFileClassifier.set_attributes_per_file_type(kml, 'S3upload', destination)

    def process_zip_rt(self):
        """
        Set realtime file destination path based on ANFOG_RT FV00 file attributes
        Check that zip contains a fv00 has already been done
        ZIP typically contains :
            - one FV00 (compulsory)
            - IMAGES (PNGs)
        all files have to be uploaded to S3
        """
        is_rt_netcdf = self.file_collection.filter_by_attribute_regex('name', AnfogFileClassifier.FV00_REGEX)
        if is_rt_netcdf is None or len(is_rt_netcdf) != 1:
            raise InvalidInputFileError(
                " Missing NetCDF or Invalid Netcdf Filename in ZIP {zip}'".format(
                    zip=os.path.basename(self.input_file))
            )
        else:
            fv00 = is_rt_netcdf[0]
            destination = AnfogFileClassifier.dest_path(fv00, 'RT')
            fv00.dest_path = os.path.join(destination, fv00.name)
            fv00.check_type = PipelineFileCheckType.FORMAT_CHECK
            # Check if on S3 mission exist
            # -if yes: need to delete previous netcdf file
            # -if not: add new entry in Harvestmissionfile.csv ;
            response = self.state_query.query_storage(destination)
            if response:  # directory exists, contains files that need to be deleted
                self.handle_previous_version('RT', destination, 'in_progress')
            else:  # path doesn't exist, mission is new
                deployment = AnfogFileClassifier.get_deployment_code(fv00)
                platform = AnfogFileClassifier.get_platform(fv00.name)
                self.set_mission_status(deployment, platform, 'in_progress')

        non_nc_files = PipelineFileCollection(f for f in self.file_collection if f.file_type is not FileType.NETCDF)
        for non_nc in non_nc_files:
            # mission transect ancillary files get check_type set to FORMAT_CHECK and publish type to UPLOAD_ONLY
            non_nc.check_type = PipelineFileCheckType.FORMAT_CHECK
            non_nc.publish_type = PipelineFilePublishType.UPLOAD_ONLY
            non_nc.dest_path = os.path.join(destination, non_nc.name)

    def set_mission_status(self, deployment, platform, message):
        """
        load Harvestmission.csv into a data frame
        if new deployment : append row with 'deployment_name, platfom_type, status'
        if update of current deployment: find the relvant data and update the status
        if check : single file submitted, should be an update. Check is to ensure deployment already exist. If not ,
        data should have been submitted with ancillary material(png, pdf...)
        :return: uodated Harvestmission.csv file with new deployment status
        """

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

    def handle_previous_version(self, mode, path, mission_status):
        """
           In RT mode: select previous version of a file that needs to be deleted (.nc and transect pngs)
                       other files are automatically overwritten
           In DM mode either - new DM : delete RT mission files
                            or
                              - update DM : delete previous .nc, other files are automatically overwritten)
         """
        # set the publishtype set according to file type: netcdf unharvest_delete,
        # everything else (png, txt, kml..) DELETE_ONLY
        previous_file_list = self.state_query.query_storage(path)

        for filename in previous_file_list.iteritems():
            if filename.endswith('.nc'):
                previous_file = PipelineFile(filename)
                self.file_collection.add(previous_file)
                previous_file.dest_path = os.path.join(path, previous_file.name)
                previous_file.publish_type = PipelineFilePublishType.DELETE_UNHARVEST
            else:
                if mode == 'RT' and re.match(AnfogFileClassifier.RT_PNG_TRANSECT_REGEX, filename):
                    # delete plot of transect results
                    previous_file = PipelineFile(filename)
                    self.file_collection.add(previous_file)
                    previous_file.dest_path = os.path.join(path, previous_file.name)
                    previous_file.publish_type = PipelineFilePublishType.DELETE
                elif mode == 'DM' and mission_status == 'delayed_mode':
                    # clear all RT files
                    previous_file = PipelineFile(filename)
                    self.file_collection.add(previous_file)
                    previous_file.dest_path = os.path.join(path, previous_file.name)
                    previous_file.publish_type = PipelineFilePublishType.DELETE

    dest_path = AnfogFileClassifier.dest_path
