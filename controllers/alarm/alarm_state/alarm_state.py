# pylint: disable=too-many-locals, too-many-branches, unidiomatic-typecheck, no-self-use
"""Alarm State"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm.calculate_alarm_trigger import CalculateAlarmTrigger
from library.alarm.format_alarm_state import FormatAlarmState
from controllers.alarm.report import percentage

class AlarmState(Common):
    """Class for AlarmState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmState class"""

        self.postgres = PostgreSQL()
        self.calc_trigger = CalculateAlarmTrigger()
        self.format_alarm = FormatAlarmState()
        self.report_pecentage = percentage.Percentage()
        super(AlarmState, self).__init__()

    def alarm_state(self):
        """
        This API is for Getting Alarm Trigger Result
        ---
        tags:
          - Alarm State
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
          - name: verbose_level
            in: query
            description: Verbose Level
            required: true
            types: integer
            examples: [10,20,30,40,50]
          - name: vessel_id
            in: query
            description: Vessel ID
            required: false
            type: string
          - name: device_id
            in: query
            description: Device ID
            required: false
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
            description: Alarm Trigger Result
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        verbose_level = int(request.args.get('verbose_level'))
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        epoch_format = request.args.get('format')

        if not device_id:
            device_id = None

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if epoch_format in ['week', 'month', "quarter", 'annual']:
            return self.report_pecentage.report_pecentage(
                verbose_level,
                vessel_id,
                epoch_format,
                flag=False
            )

        data['data'] = []

        # end_time = time.time()

        if epoch_format == "day":
            key = epoch_format
            # start = 1

        else:
            key = "hours"
            # start = 8

        # start_time = self.timediff_update(end_time, start, key=key)

        if verbose_level:

            alarm_triggers = self.convert_verbose_level(verbose_level)

            if alarm_triggers:

                trigger_ids = [alarm_trigger['alarm_trigger_id']
                               for alarm_trigger in alarm_triggers]

                results = self.get_alarm_state(tuple(trigger_ids), vessel_id, key)
                if results:
                    datas = results
                else:
                    data['alert'] = "No Alarm Available"
                    data['status'] = 'ok'

                    return self.return_data(data)
                # datas = self.calc_trigger.calculate_trigger(
                #     trigger_ids,
                #     start_time,
                #     end_time,
                #     vessel_id=vessel_id,
                #     device_id=device_id
                # )

                # if type(datas) == list:

                #     datas = self.get_datas(datas, epoch_format, end_time)

                #     if not epoch_format:
                #         datas = self.format_alarm.filter_current_status(datas)

                # else:
                #     data['alert'] = datas
                #     data['status'] = 'ok'
                    # return self.return_data(data)

            else:

                data['alert'] = "No Alarm Available"
                data['status'] = 'ok'

                return self.return_data(data)

        data['data'] = datas
        data['status'] = 'ok'

        return self.return_data(data)


    def convert_verbose_level(self, verbose):
        """Get All Alarm Triggers by Verbose Level"""

        assert verbose, "Verbose is required."

        # DATA
        sql_str = "SELECT alarm_trigger_id FROM alarm_trigger"
        sql_str += " WHERE alarm_type_id IN"
        sql_str += " (SELECT alarm_type_id FROM alarm_type"
        sql_str += " WHERE alarm_value <= {0})".format(verbose)
        sql_str += " AND alarm_enabled = 'T'"

        alarm_types = self.postgres.query_fetch_all(sql_str)

        if alarm_types:

            return alarm_types

        return 0

    def get_datas(self, datas, epoch_format, end_time):
        """ Set datas """

        for alarm in datas:
            alarm_result = alarm['results']

            if alarm_result and not alarm['err_message']:
                if not epoch_format:
                    self.format_alarm.get_current_alarm(alarm_result)

                else:
                    self.format_alarm.get_alarm24(alarm_result, end_time)

        return datas

    def get_alarm_state(self, at_ids, vessel_id, key):
        """ Return Alarm Data for current and 24 hours """
        today = time.time()
        format_date = self.days_update(today, 1, True)
        epoch_date = self.days_update(format_date, 1)

        sql_str = "SELECT alarm_description, alarm_trigger_id, alarm_type,"
        sql_str += " err_message, results FROM alarm_state"
        sql_str += " WHERE alarm_trigger_id IN {0}".format(at_ids)
        sql_str += " AND epoch_date='{0}' AND category='{1}'".format(int(epoch_date), key)

        if vessel_id:
            sql_str += " AND vessel_id='{0}'".format(vessel_id)

        alarms = self.postgres.query_fetch_all(sql_str)

        return alarms
