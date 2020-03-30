"""Create Alarm Condition"""
import json
import time
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from controllers.alarm.alarm_conditions.validate_alarm_condition import ValidateAlarmCondition

class CreateAlarmCondition(Common):
    """Class for CreateAlarmCondition"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateAlarmCondition class"""

        self.postgres = PostgreSQL()
        self.validate_condition = ValidateAlarmCondition()
        super(CreateAlarmCondition, self).__init__()

    def create_alarm_condition(self):
        """
        This API is for Creating Alarm Condition
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
          - name: query
            in: body
            description: Alarm Condition
            required: true
            schema:
              id: AlarmCondition
              properties:
                comment:
                    type: string
                operator_id:
                    type: string
                parameters:
                    type: json
                    example: {}
        responses:
          500:
            description: Error
          200:
            description: Alarm Condition
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        validate = self.validate_condition.validate_alarm_condition(query_json)

        if validate:

            data['alert'] = validate['alert']
            data['status'] = 'Failed'

            return self.return_data(data)

        if not self.insert_alarm_condition(query_json):

            data["alert"] = "Please check your query! | Alarm Condition is Already Exist."
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm condition successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_alarm_condition(self, query_json):
        """Insert Alarm Condition"""

        query_json['parameters'] = json.dumps(query_json['parameters'])
        query_json['created_on'] = time.time()

        if self.postgres.insert('alarm_condition', query_json, 'alarm_condition_id'):
            return 1

        return 0
