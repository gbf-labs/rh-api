"""Alarm Condition Operator"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class AlarmConditionOperator(Common):
    """Class for AlarmConditionOperator"""
    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmConditionOperator class"""

        self.postgres = PostgreSQL()
        super(AlarmConditionOperator, self).__init__()

    def alarm_condition_operators(self):
        """
        This API is for Getting Alarm Condition Operators
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
            data['status'] = "Failed"

            # RETURN ALERT
            return self.return_data(data)

        data['data'] = []

        #GET DATA
        datas = self.get_alarm_condition_operators()

        data_formatted = []

        for dta in datas['rows']:

            formatted = [{
                "value": dta['alarm_coperator_id'],
                "label": dta['label'],

                "operator": dta['operator'],
                "param_num": dta['param_num']
            }]

            data_formatted.append({
                "label" : dta['opgroup'],
                "options": formatted
            })

        if datas:
            rows = datas['rows']

        else:
            rows = []

        final_data = rows
        total_count = len(final_data)
        data['data'] = data_formatted
        data['total_rows'] = total_count
        data['status'] = 'ok'

        return self.return_data(data)

    def get_alarm_condition_operators(self):
        """Get All Alarm Condition Operators"""

        # DATA
        sql_str = "SELECT * FROM alarm_coperator"

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        return data

    # GET ALARM CONDITION
    def get_alarm_condition_operator(self, alarm_coperator_id):
        """Get Alarm Condition Operator"""

        assert alarm_coperator_id, "Alarm Condition Operator ID is required."

        # DATA
        alarm_coperator = []
        sql_str = "SELECT * FROM alarm_coperator"
        sql_str += " WHERE alarm_coperator_id={0}".format(alarm_coperator_id)
        alarm_coperator = self.postgres.query_fetch_one(sql_str)

        return alarm_coperator
