"""Alarm Condition Parameters"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from controllers.alarm.alarm_values.alarm_values import AlarmValues
from controllers.alarm.alarm_conditions.alarm_conditions import AlarmConditions

class AlarmConditionParameters(Common):
    """Class for AlarmConditionParameters"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmConditionParameters class"""

        self.postgres = PostgreSQL()
        self.alarm_value = AlarmValues()
        self.alarm_condition = AlarmConditions()
        super(AlarmConditionParameters, self).__init__()

    def alarm_condition_parameters(self):
        """
        This API is for Getting Alarm Condition Parameters
        ---
        tags:
          - Alarm Conditions
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
            description: Alarm Conditions
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

        #GET DATA
        datas = self.get_alarm_param_data()

        if datas:
            rows = datas['rows']

        else:
            rows = []

        final_data = rows
        total_count = len(final_data)

        data['data'] = final_data
        data['total_rows'] = total_count
        data['status'] = 'ok'

        return self.return_data(data)

    def get_alarm_param_data(self):
        """Get Alarm Condition Parameter"""

        data = {}

        conditions = []
        all_conditions = []

        alarm_conditions = self.alarm_condition.get_alarm_conditions()

        for condition in alarm_conditions['rows']:
            conditions.append({
                "label": condition['comment'],
                "value": condition['alarm_condition_id'],
                "type": "conditions"
            })

        all_conditions.append({
            "label": "Alarm Condition",
            "options": conditions
        })

        values = []
        all_values = []
        alarm_values = self.alarm_value.get_alarm_values()

        for value in alarm_values['rows']:
            values.append({
                "value": value['alarm_value_id'],
                "label": value['name'],
                "type": "values"
            })

        all_values.append({
            "label": "Alarm Value",
            "options": values
        })

        data['rows'] = all_values + all_conditions

        return data
