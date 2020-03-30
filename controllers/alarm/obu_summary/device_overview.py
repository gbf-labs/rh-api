# pylint: disable=no-self-use, too-many-locals
"""Device Overview"""
import time
from flask import  request
from library.common import Common
from library.alarm import calculate_alarm_trigger
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.unit_conversion import UnitConversion

class DeviceOverview(Common):
    """Class for DeviceOverview"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeviceOverview class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.unit_conversion = UnitConversion()
        self.calc = calculate_alarm_trigger.CalculateAlarmTrigger()
        super(DeviceOverview, self).__init__()

    def device_overview(self):
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
          - name: format
            in: query
            description: Epoch Start Format
            required: false
            type: string
        responses:
          500:
            description: Error
          200:
            description: Alarm Device Overview
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')
        epoch_format = request.args.get('format')

        # CHECK TOKEN
        if not self.validate_token(token, userid):
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'
            return self.return_data(data)

        alarm_types = self.get_alarm_types()

        ats = self.get_alarm_trigger()

        devices = self.couch_query.get_all_devices(vessel_id)

        standard_time = self.epoch_day(time.time())

        epoch_time = time.time()

        temp_data = []

        start_date = self.get_start_date(epoch_format)

        if not start_date and epoch_format not in ["day", "hours"]:

            data['alert'] = "Invalid format!"
            data['status'] = 'Failed'

            return self.return_data(data)

        for device in devices:

            if device['doc']['device'] in ['PARAMETERS', 'NTWCONF', 'NTWPERF1']:

                continue

            row = {}
            row['device'] = device['doc']['device']
            row['name'] = device['doc']['device']
            row['Alert'] = 0
            row['Critical'] = 0
            row['Warning'] = 0
            row['Info'] = 0
            row['Debug'] = 0
            for atrigger in ats:

                trigger_type = self.get_alarm_type_name(alarm_types, atrigger['alarm_type_id'])

                at_id = atrigger['alarm_trigger_id']
                device_id = device['id']

                datas = self.calc.calculate_trigger([at_id], standard_time,
                                                    epoch_time, vessel_id=vessel_id,
                                                    device_id=device_id)

                if not datas == "No Alarm Trigger found.":

                    datas_index_0 = datas[0]
                    len_datas = datas_index_0['results']
                    if len_datas:

                        row[trigger_type] = 1

                    if epoch_format in ['week', 'month', "quarter", 'annual']:

                        sql_str = "SELECT COUNT(alarm_trigger_id) FROM alarm_data "
                        sql_str += "WHERE device_id='{0}' ".format(device_id)
                        sql_str += "AND epoch_date > {0} ".format(start_date)
                        sql_str += "AND epoch_date < {0}".format(epoch_time)

                        res = self.postgres.query_fetch_one(sql_str)

                        row[trigger_type] = row[trigger_type] + res['count']

            temp_data.append(row)

        final_data = {}
        final_data['data'] = temp_data
        final_data['status'] = 'ok'

        return self.return_data(final_data)

    def get_alarm_trigger(self):
        """Return Alarm Trigger"""

        sql_str = "SELECT * FROM alarm_trigger WHERE alarm_enabled=true"

        res = self.postgres.query_fetch_all(sql_str)

        return res

    def get_alarm_types(self):
        """Return Alarm Types"""

        # DATA
        sql_str = "SELECT * FROM alarm_type"

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        return data

    def get_alarm_type_name(self, a_types, alarm_type_id):
        """Return Alarm Type Name"""

        for a_type in a_types['rows']:

            if a_type['alarm_type_id'] == alarm_type_id:

                return a_type['alarm_type']

        return 0

    def get_start_date(self, type_format):
        """Return Start Date"""

        start_date = 0

        if type_format not in ["annual", "quarter", "week", "month"]:
            return 0

        if type_format.lower() == "week":
            start_date = self.days_update(time.time(), 7)

        elif type_format.lower() == "month":
            start_date = self.datedelta(time.time(), days=1, months=1)

        elif type_format.lower() in ["annual", "quarter"]:
            start_date = self.datedelta(time.time(), days=1, years=1)

        return start_date
