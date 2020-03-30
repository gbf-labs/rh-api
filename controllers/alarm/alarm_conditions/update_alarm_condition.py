"""Update Alarm Condition"""
import json
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from controllers.alarm.alarm_conditions.validate_alarm_condition import ValidateAlarmCondition

class UpdateAlarmCondition(Common):
    """Class for UpdateAlarmCondition"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateAlarmCondition class"""

        self.postgres = PostgreSQL()
        self.validate_condition = ValidateAlarmCondition()
        super(UpdateAlarmCondition, self).__init__()

    def update_alarm_condition(self):
        """
        This API is for Updating Alarm Condition
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
            description: Updating Alarm Condition
            required: true
            schema:
              id: Updating Alarm Condition
              properties:
                alarm_condition_id:
                    type: string
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
            description: Updating Alarm Condition
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

        if not self.edit_alarm_condition(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm condition successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)


    def edit_alarm_condition(self, query_json):
        """Update Alarm Condition"""

        query_json['parameters'] = json.dumps(query_json['parameters'])
        query_json['update_on'] = time.time()

        # GET ALARM CONDITION ID
        alarm_condition_id = query_json['alarm_condition_id']

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "alarm_condition_id",
            "con": "=",
            "val": alarm_condition_id
            })

        # REMOVE KEYS
        query_json = self.remove_key(query_json, "alarm_condition_id")

        # UPDATE ALARM CONDITION
        if self.postgres.update('alarm_condition', query_json, conditions):
            # RETURN
            return 1

        # RETURN
        return 0
