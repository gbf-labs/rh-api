# pylint: disable=too-many-statements, too-many-branches, too-many-return-statements
"""Validate Alarm Value"""
from library.common import Common
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL

class ValidateAlarmValue(Common):
    """Class for ValidateAlarmValue"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for ValidateAlarmValue class"""

        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(ValidateAlarmValue, self).__init__()

    # VALIDATE INPUTS
    def validate_alarm_value(self, query_json):
        """Validate Alarm Value"""

        data = {}

        if not query_json['name']:

            data["alert"] = "Name cannot be empty!"

            return data

        if not query_json['option']:

            data["alert"] = "Option cannot be empty!"

            return data

        if query_json['vessel']:

            for vessel in query_json['vessel'].split(","):

                values = self.couch_query.get_complete_values(
                    vessel,
                    "PARAMETERS")

                if values:

                    vessel_name = values['PARAMETERS']['INFO']['VESSELNAME']

                else:

                    data["alert"] = "No Vessel found."
                    return data

                if query_json['device']:

                    column = "device"

                    for device in query_json['device'].split(","):

                        validate = self.check_alarm_data(column, device, vessel)

                        if not validate:

                            data["alert"] = "No Device found under {0}.".format(vessel_name)
                            return data

                if query_json['module']:

                    column = "module"

                    for module in query_json['module'].split(","):

                        validate = self.check_alarm_data(column, module, vessel)

                        if not validate:

                            data["alert"] = "No Module found under {0}.".format(vessel_name)
                            return data

                if query_json['option']:

                    column = "option"

                    for option in query_json['option'].split(","):

                        validate = self.check_alarm_data(column, option, vessel)

                        if not validate:

                            data["alert"] = "No Option found under {0}.".format(vessel_name)
                            return data

        if query_json['device']:

            column = "device"

            for device in query_json['device'].split(","):

                validate = self.check_alarm_data(column, device)

                if not validate:

                    data["alert"] = "No Device found."
                    return data

        if query_json['device_type']:

            column = "device_type"

            for device_type in query_json['device_type'].split(","):

                validate = self.check_alarm_data(column, device_type)

                if not validate:

                    data["alert"] = "No Device found."
                    return data

        if query_json['module']:

            column = "module"

            for module in query_json['module'].split(","):

                validate = self.check_alarm_data(column, module)

                if not validate:

                    data["alert"] = "No Module found."
                    return data

        if query_json['option']:

            column = "option"

            for option in query_json['option'].split(","):

                validate = self.check_alarm_data(column, option)

                if not validate:

                    data["alert"] = "No Option found"
                    return data

        if query_json['device'] and query_json['device_type']:

            for device in query_json['device'].split(","):

                if device in ['COREVALUES', 'FAILOVER', 'PARAMETERS', 'NTWCONF']:

                    data["alert"] = "No Device Type under {0}".format(query_json['device'])

                else:

                    for device_type in query_json['device_type'].split(","):
                        if not self.check_device_type(device, device_type):
                            data['alert'] = "No Device Type found on Device"

            return data

        return 0

    def check_alarm_data(self, column, value, vessel=None):
        """Validate Alarm Data"""

        if column == "device_type":

            table = "device"

        else:
            table = column

        # DATA
        sql_str = "SELECT * FROM {0}".format(table)
        sql_str += " WHERE {0} ILIKE '{1}'".format(column, value)

        if vessel:
            sql_str += " AND vessel_id ILIKE '{0}'".format(vessel)

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        if datas:
            return data

        return 0

    def check_device_type(self, device, device_type):
        """Validate Device Type"""

        # DATA
        sql_str = "SELECT * FROM device"
        sql_str += " WHERE device ILIKE '{0}'".format(device)
        sql_str += " AND device_type ILIKE '{0}'".format(device_type)

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        if datas:
            return data

        return 0
