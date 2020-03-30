# pylint: disable=too-many-locals
"""OBU Summary"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.unit_conversion import UnitConversion

class ObuSummary(Common):
    """Class for ObuSummary"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for ObuSummary class"""

        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.unit_conversion = UnitConversion()
        super(ObuSummary, self).__init__()

    def obu_summary(self):
        """
        This API is for Getting OBU Summary per Vessel
        ---
        tags:
          - Alarm OBU Summary
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
          - name: vessel_id
            in: query
            description: Vessel ID
            required: true
            type: string
        responses:
          500:
            description: Error
          200:
            description: Alarm OBU Summary
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')

        # CHECK TOKEN
        if not self.validate_token(token, userid):
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

        data = {}

        system = self.couch_query.get_system(vessel_id)

        system_info = {}

        if system["rows"]:

            row = system["rows"][0]["doc"]
            # START TIME
            start_time = time.localtime(row["data"]["start_time"])
            start_time = time.strftime("%d %b %Y %H:%M:%S %Z", start_time)

            # END TIME
            end_time = time.localtime(row["data"]["end_time"])
            end_time = time.strftime("%d %b %Y %H:%M:%S %Z", end_time)

            # TIME DELTA
            runtime_overall = self.time_span(row["data"]["end_time"], row["data"]["start_time"])

            # DEVICE
            device_list = self.couch_query.get_device(vessel_id)

            # REMOVE DATA
            data_to_remove = ['PARAMETERS', 'COREVALUES', 'FAILOVER', 'NTWCONF']
            device_list = self.remove_data(device_list, data_to_remove)

            # COREVALUES
            corevalues = self.couch_query.get_complete_values(
                vessel_id,
                "COREVALUES",
                flag='one_doc'
            )

            days = int(row["data"]["end_time"] - row["data"]["start_time"]) // (24 * 3600) + 1

            table_size = float(row["data"]["data_size"]) / days

            table_size = format(table_size, '.4f')

            database_size = format(row["data"]["data_size"], '.4f')

            parameters = self.couch_query.get_complete_values(
                vessel_id,
                "PARAMETERS"
            )

            imo = parameters['PARAMETERS']['INFO']['IMO']

            system_info["first_timestamp"] = start_time
            system_info["last_timestamp"] = end_time
            system_info["runtime_overall"] = runtime_overall
            system_info["datapoints"] = row["data"]["doc_count"]
            system_info["devices"] = len(device_list)
             # 3 IS 'COREVALUES', 'FAILOVER', 'NTWCONF'
            system_info["monitored_parameters"] = len(device_list) + 3
            system_info["database_size"] = str(database_size) + " MB"
            system_info["table_size"] = str(table_size) + " MB"
            system_info["main_loop_time"] = str(int(float(
                corevalues["value"]["COREVALUES"]["CoreInfo"]["MainLoopTime"]))) + " Seconds"
            system_info["imo"] = imo

            if "ui_version" in row["data"].keys():
                system_info["ui_version"] = row["data"]["ui_version"]

            if "api_version" in row["data"].keys():
                system_info["api_version"] = row["data"]["api_version"]

            if "backend_version" in row["data"].keys():
                system_info["backend_version"] = row["data"]["backend_version"]

        data['data'] = system_info

        self.get_vessel_device(vessel_id)

        data['status'] = 'ok'

        return self.return_data(data)

    def get_vessel_summary(self, vessel):
        """Return Vessel Summary"""

        data = {}
        if vessel:

            values = self.couch_query.get_complete_values(
                vessel,
                "COREVALUES",
                flag='all')

            if values:

                timestamp = [value['timestamp'] for value in values]

                data['min_timestamp'] = min(timestamp)
                data['max_timestamp'] = max(timestamp)

                return data

        return 0

    def get_vessel_device(self, vessel):
        """Return Vessel Device"""

        # DATA
        devices = []
        sql_str = "SELECT * FROM device"
        sql_str += " WHERE vessel_id='{0}'".format(vessel)
        sql_str += " AND device NOT IN ('PARAMETERS', 'COREVALUES', 'FAILOVER', 'NTWCONF')"
        devices = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = devices

        return data
