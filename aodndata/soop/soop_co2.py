import datetime
import os

from aodncore.pipeline import FileClassifier
from aodncore.pipeline import HandlerBase, PipelineFile, PipelineFilePublishType, PipelineFileCheckType, FileType
from aodncore.pipeline import PipelineFileCollection
from aodncore.pipeline.exceptions import InvalidInputFileError, InvalidFileFormatError, InvalidFileNameError

import soop_co2_nrt_nc_generator
from .ship_callsign import ship_callsign_list

VALID_PROJECT = ['IMOS', 'FutureReefMap', 'SOOP-CO2_RT']
VESSEL_CODE = {'AA': 'VNAA',
               'IN': 'VLMJ'}


def def_project(src_file):
    """
    Define project name according to file name or extension
    Differentiate IMOS SOOP-CO2 RealTime from Delayed Mode and Future_Reef_MAP files
    eg : (DM) IMOS_SOOP-CO2_GST_20121027T045200Z_VLHJ_FV01.nc
         (DM) FutureReefMap_GST_20140530T185029Z_9V2768_FV01.nc
         <Project_Name>_<<Facility-Code>>_<Data-Code>_<Start-date>_<Platform-Code>_FV<File-Version>.nc
         (RT) IN_2017-165-0000dat.txt
          <Vessel_code>_yyyy-ddd-hhmmdat.tx
          :type src_file: object
    return: destination relative path to destination folder.
    eg: 'IMOS/SOOP/SOOP-CO2/VNAA_Aurora-Australis/2017/AA1617_V3/'
    """

    if src_file.name.endswith('.nc'):
        fields = FileClassifier._get_file_name_fields(src_file.name, min_fields=5)
        if 'FV00' in src_file.name:
            return fields[1] + '_RT'  # <Facility-Name + RTnc suffix>
        else:
            return fields[0]  # <Project-Name>
    else:
        raise InvalidFileFormatError(
            "'{name}'is not a valid RT CO2 data (*dat.txt) or not a NetCDF file.".format(
                name=src_file.name)
        )


def dest_path_soop_co2(src_file):

    dir_list = []
    project = def_project(src_file)
    ship_callsign_ls = ship_callsign_list()

    if project not in VALID_PROJECT:
        raise InvalidFileNameError(
            "Invalid project name '{project}'. "
            "Project should be IMOS, SOOP-CO2_RT or Future_Reef_MAP".format(project=project))

    if project in ['IMOS', 'SOOP-CO2_RT']:
        fields = FileClassifier._get_file_name_fields(src_file.name)
        ship_code = fields[4]
        if ship_code not in ship_callsign_ls:
            raise InvalidFileNameError(
                "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

        project_base = 'IMOS'
        facility = fields[1][:4]
        sub_facility = fields[1]
        platform = "{ship_code}_{ship_name}".format(ship_code=ship_code, ship_name=ship_callsign_ls[ship_code])
        dir_list.extend([project_base, facility, sub_facility, platform])

    if project == 'FutureReefMap':
        fields = FileClassifier._get_file_name_fields(src_file.name, min_fields=5)
        ship_code = fields[3]
        if ship_code not in ship_callsign_ls:
            raise InvalidFileNameError(
                "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

        dir_list.append('Future_Reef_MAP')
        data_type = 'underway'
        dir_list.extend([data_type, ship_callsign_ls[ship_code]])

    if project in ['IMOS', 'FutureReefMap']:
        att_list = FileClassifier._get_nc_att(src_file.src_path, ['cruise_id', 'time_coverage_start'])
        year = att_list[1][:4]
        cruise_id = att_list[0]
        dir_list.extend([year, cruise_id])

    if project == 'SOOP-CO2_RT':
        data_type = 'REALTIME'
        time_start = FileClassifier._get_nc_att(src_file.src_path, 'time_coverage_start')
        year = time_start[:4]
        month = time_start[5:7]
        month = month.lstrip('0')
        dir_list.extend([data_type, year, month])

    return FileClassifier._make_path(dir_list)


def archive_path_soop_co2(src_file):
    """
    Generate archive path for RT file based on vessel_code
        eg:IN_2017-165-0000dat.txt
          <Vessel_code>_yyyy-ddd-hhmmdat.txt
    :return: relative archive path- full path, including file name
    eg: 'IMOS/SOOP/SOOP-CO2/VLMJ_Investigator/REALTIME/2018/1/IN_2018-022-0000dat.txt'
    """
    dir_list = []
    project = 'IMOS'
    facility = 'SOOP'
    sub_facility = 'SOOP-CO2'
    data_type = 'REALTIME'
    dir_list.extend([project, facility, sub_facility])
    ship_callsign_ls = ship_callsign_list()
    fields = FileClassifier._get_file_name_fields(os.path.basename(src_file), min_fields=2)
    if fields[0] in VESSEL_CODE:
        ship_code = VESSEL_CODE[fields[0]]
    else:
        raise InvalidFileNameError(
            "File {file} has an invalid vessel code or is not a valid SOOP-CO2 realtime file".format(
                file=os.path.basename(src_file))
        )
    platform = "{ship_code}_{ship_name}".format(ship_code=ship_code, ship_name=ship_callsign_ls[ship_code])
    dir_list.extend([platform, data_type])
    year = int(fields[1][:4])
    dir_list.append(year)
    jday = int(fields[1][5:8])
    if not (jday in range(0, 366)) or year < 2017:
        raise InvalidFileNameError(
            "Failed extracting valid [year, day] from file {file}".format(file=os.path.basename(src_file))
        )

    # Determine month from julian day (1-365). Leap year taken into account
    year_to_ordinal = datetime.date(year, 1, 1).toordinal() + jday - 1
    month = datetime.date.fromordinal(year_to_ordinal).month
    dir_list.append(month)
    dir_list.append(os.path.basename(src_file))

    return FileClassifier._make_path(dir_list)


class SoopCo2Handler(HandlerBase):
    """
    Handler for data from IMOS SOOP CO2(DM, RT) and Future Reef Map Project.
    It handles the following file types:
         * ZIP;
         * NetCDF;
         * TXT;
    """
    dest_path = dest_path_soop_co2
    archive_path = archive_path_soop_co2

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
            set_nc_dest_path = dest_path_soop_co2(nc)
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
            set_nc_dest_path = dest_path_soop_co2(nrt_nc_file)
            nrt_nc_file.dest_path = os.path.join(set_nc_dest_path, nrt_nc_file.name)

        elif self.file_type is FileType.NETCDF:
            # single NetCDF file
            nc = self.file_collection[0]
            nc_dest_path = dest_path_soop_co2(nc)
            nc.dest_path = os.path.join(nc_dest_path, nc.name)

        else:
            raise InvalidInputFileError(
                "File format '{file}' is invalid. Should be a SOOP-CO2 realtime file (*dat.txt) " 
                "or a Delayed Mode zip archive or NetCDF file.".format(file=self.input_file)
            )
