# pylint: disable=too-many-locals, unidiomatic-typecheck
"""Alarm State Overview"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm.format_alarm_state import FormatAlarmState
from library.alarm.calculate_alarm_trigger import CalculateAlarmTrigger
from controllers.alarm.report import percentage

class AlarmStateOverview(Common):
    """Class for AlarmStateOverview"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmStateOverview class"""

        self.postgres = PostgreSQL()
        self.format_alarm = FormatAlarmState()
        self.calc_trigger = CalculateAlarmTrigger()
        self.report_pecentage = percentage.Percentage()
        super(AlarmStateOverview, self).__init__()

    def alarm_state_overview(self):
        """
        This API is for Getting Alarm State by Vessel and Device overview
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
          - name: vessel_id
            in: query
            description: Vessel ID
            required: true
            types: string
          - name: device_id
            in: query
            description: Device ID
            required: true
            types: string
          - name: alarm_value
            in: query
            description: Alarm Type Value
            required: true
            types: integer
          - name: format
            in: query
            description: Epoch Start Format
            required: false
            type: string

        responses:
          500:
            description: Error
          200:
            description: Vessel Alarm State Overview
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        alarm_value = request.args.get('alarm_value')
        epoch_format = request.args.get('format')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if epoch_format in ['week', 'month', 'quarter', 'anual']:
            return self.report_pecentage.report_pecentage(
                alarm_value,
                vessel_id,
                epoch_format,
                device_id=device_id,
                flag=True
            )

        data['data'] = []

        end_time = time.time()

        if epoch_format:
            key = epoch_format
            start = 1

        else:

            key = "hours"
            start = 8

        start_time = self.timediff_update(end_time, start, key=key)

        trigger = self.get_trigger(alarm_value)

        if trigger:

            trigger_id = [trigger['alarm_trigger_id']]

            datas = self.calc_trigger.calculate_trigger(trigger_id, start_time,
                                                        end_time, vessel_id, device_id)

            if type(datas) == list:
                for alarm in datas:
                    alarm_result = alarm['results']

                    if alarm_result and not alarm['err_message']:
                        if not epoch_format:
                            self.format_alarm.get_current_alarm(alarm_result)

                        else:
                            self.format_alarm.get_alarm24(alarm_result, end_time)
            else:
                data['alert'] = datas
                data['status'] = 'Failed'
                return self.return_data(data)

        else:
            data['alert'] = "No Alarm Available"
            data['status'] = 'Failed'
            return self.return_data(data)

        total_count = len(datas)
        data['total_rows'] = total_count
        data['data'] = datas
        data['status'] = 'ok'

        return self.return_data(data)


    def get_trigger(self, alarm_value):
        """Get Alarm Trigger"""

        assert alarm_value, "Alarm Value is required."

        # DATA
        sql_str = "SELECT alarm_trigger_id FROM alarm_trigger"
        sql_str += " WHERE alarm_type_id IN"
        sql_str += " (SELECT alarm_type_id FROM alarm_type"
        sql_str += " WHERE alarm_value = {0})".format(alarm_value)
        sql_str += " AND alarm_enabled = 'T'"

        alarm_triggers = self.postgres.query_fetch_one(sql_str)

        if alarm_triggers:

            return alarm_triggers

        return 0
