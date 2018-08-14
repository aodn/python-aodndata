from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import InvalidFileNameError, InvalidFileFormatError
from ship_callsign import ship_callsign_list
import datetime
import os


class SoopCo2FileClassifier(FileClassifier):
    VALID_PROJECT = ['IMOS', 'FutureReefMap', 'SOOP-CO2_RT']
    VESSEL_CODE = {'AA': 'VNAA',
                   'IN': 'VLMJ'}
    ship_callsign_ls = ship_callsign_list()

    @classmethod
    def def_project(cls, src_file):
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
            fields = cls._get_file_name_fields(src_file.name, min_fields=5)
            if 'FV00' in src_file.name:
                return fields[1] + '_RT'  # <Facility-Name + RTnc suffix>
            else:
                return fields[0]  # <Project-Name>
        else:
            raise InvalidFileFormatError(
                "'{name}'is not a valid RT CO2 data (*dat.txt) or not a NetCDF file.".format(
                    name=src_file.name)
            )

    @classmethod
    def dest_path(cls, src_file):

        dir_list = []
        project = cls.def_project(src_file)
        if project not in cls.VALID_PROJECT:
            raise InvalidFileNameError(
                "Invalid project name '{project}'. "
                "Project should be IMOS, SOOP-CO2_RT or Future_Reef_MAP".format(project=project))

        if project in ['IMOS', 'SOOP-CO2_RT']:
            fields = cls._get_file_name_fields(src_file.name)
            ship_code = fields[4]
            if ship_code not in cls.ship_callsign_ls:
                raise InvalidFileNameError(
                    "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

            project_base = 'IMOS'
            facility = fields[1][:4]
            sub_facility = fields[1]
            platform = "%s_%s" % (ship_code, cls.ship_callsign_ls[ship_code])
            dir_list.extend([project_base, facility, sub_facility, platform])

        if project == 'FutureReefMap':
            fields = cls._get_file_name_fields(src_file.name, min_fields=5)
            ship_code = fields[3]
            if ship_code not in cls.ship_callsign_ls:
                raise InvalidFileNameError(
                    "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

            dir_list.append('Future_Reef_MAP')
            data_type = 'underway'
            dir_list.extend([data_type, cls.ship_callsign_ls[ship_code]])

        if project in ['IMOS', 'FutureReefMap']:
            att_list = cls._get_nc_att(src_file.src_path, ['cruise_id', 'time_coverage_start'])
            year = att_list[1][:4]
            cruise_id = att_list[0]
            dir_list.extend([year, cruise_id])

        if project == 'SOOP-CO2_RT':
            data_type = 'REALTIME'
            time_start = cls._get_nc_att(src_file.src_path, 'time_coverage_start')
            year = time_start[:4]
            month = time_start[5:7]
            month = month.lstrip('0')
            dir_list.extend([data_type, year, month])

        return cls._make_path(dir_list)

    @classmethod
    def archive_path(cls, src_file):
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
        fields = cls._get_file_name_fields(os.path.basename(src_file), min_fields=2)
        if fields[0] in cls.VESSEL_CODE:
            ship_code = cls.VESSEL_CODE[fields[0]]
        else:
            raise InvalidFileNameError(
                "File {file} has an invalid vessel code or is not a valid SOOP-CO2 realtime file".format(
                    file=os.path.basename(src_file))
            )
        platform = "%s_%s" % (ship_code, cls.ship_callsign_ls[ship_code])
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

        return cls._make_path(dir_list)
