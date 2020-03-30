# pylint: disable=too-many-locals
"""Alarm Value Data"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from controllers.cron.update_device_state import UpdateDeviceState

class AlarmValueData(Common):
    """Class for AlarmValueData"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmValueData class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.device_state = UpdateDeviceState()
        super(AlarmValueData, self).__init__()

    def alarm_value_data(self):
        """
        This API is for Getting Alarm Value
        ---
        tags:
          - Alarm Values
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: userid
            in: header
            description: User ID
            required: true
            type: string

        responses:
          500:
            description: Error
          200:
            description: Alarm Value
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)



        data['data'] = []

        vessels = self.get_all_vessels()

        keys = ['device', 'device_type', 'module', 'option']

        datas = []

        for key in keys:

            alarm_data = self.get_alarm_datas(key)

            format_data = self.data_filter(alarm_data, key)

            if key == "device":
                devices = format_data

            if key == "device_type":
                device_types = format_data

            if key == "module":
                modules = format_data

            if key == "option":
                options = format_data

        if datas:
            rows = datas

        else:
            rows = []

        datas = rows
        data['vessels'] = vessels
        data['devices'] = devices
        data['modules'] = modules
        data['options'] = options
        data['device_types'] = device_types
        data['status'] = 'ok'

        return self.return_data(data)

    def get_alarm_datas(self, key):
        """Get Alarm Datas"""
        if key:

            if key == "device_type":

                table = "device"

            else:
                table = key

            # DATA
            sql_str = "SELECT DISTINCT {0} FROM {1}".format(key, table)

            datas = self.postgres.query_fetch_all(sql_str)

            data = {}

            k = "{0}s".format(key)

            temp_data = [temp_data[key] for temp_data in datas]

            data[k] = temp_data

        return data

    def get_all_vessels(self):
        """Get All Vessels"""

        vessel_list = []

        vessels = self.couch_query.get_vessels()
        if vessels:

            for item in vessels:
                vessel_name = self.couch_query.get_complete_values(
                    item['id'],
                    "PARAMETERS"
                    )

                if vessel_name:
                    vessel_name = vessel_name['PARAMETERS']['INFO']['VESSELNAME']
                else:
                    vessel_name = "Vessel Not Found"

                vessel_list.append({
                    "label": vessel_name,
                    "value": item['id']
                    })

            return vessel_list

        return ''
