from aodncore.pipeline import FileClassifier
from aodncore.pipeline.exceptions import InvalidFileNameError

from ship_callsign import ship_callsign_list


class SoopBaFileClassifier(FileClassifier):
    ship_callsign_ls = ship_callsign_list()

    @classmethod
    def dest_path(cls, src_file):

        dir_list = []
        fields = cls._get_file_name_fields(src_file.name)
        ship_code = fields[4]

        if ship_code not in cls.ship_callsign_ls:
            raise InvalidFileNameError(
                "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

        project = fields[0]
        facility = fields[1][:4]
        sub_facility = fields[1]
        platform = "%s_%s" % (ship_code, cls.ship_callsign_ls[ship_code])
        dir_list.extend([project, facility, sub_facility, platform])

        deployment_id = cls.get_deployment_id(src_file, ship_code)

        dir_list.append(deployment_id)
        return cls._make_path(dir_list)

    @classmethod
    def archive_path(cls, src_file):
        """Define the archive path based on info from NetCDF"""
        dir_list = []
        fields = cls._get_file_name_fields(src_file.name)
        ship_code = fields[4]
        if ship_code not in ship_callsign_list():
            raise InvalidFileNameError(
                "Missing vessel callsign in file name '{name}'.".format(name=src_file.name))

        project = fields[0]
        facility = fields[1][:4]
        sub_facility = fields[1]
        raw_folder = 'raw'
        platform = "%s_%s" % (ship_code, cls.ship_callsign_ls[ship_code])
        dir_list.extend([project, facility, sub_facility, raw_folder, platform])

        deployment_id = cls.get_deployment_id(src_file, ship_code)
        dir_list.append(deployment_id)
        return cls._make_path(dir_list)

    @classmethod
    def get_deployment_id(cls, src_file, ship_code):
        """
        harmonise way shipcallsign are written in  deployment codes: replace underscore by hyphen
        deployment_id format : shipcallsign_datestart-dateend
        get_nc_att will raise a n exception if the attribute is missing
        :param src_file:
        :param ship_code:
        :return: deployment_id
        """

        deployment_id = cls._get_nc_att(src_file.src_path, 'deployment_id')
        name_parts = deployment_id.split('_')

        if len(name_parts) >= 3:
            deployment_id = "%s_%s" % (cls.ship_callsign_ls[ship_code], name_parts[-1])

        return deployment_id
