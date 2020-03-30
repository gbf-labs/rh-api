"""Update Alarm Value"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from controllers.alarm.alarm_values.validate_alarm_value import ValidateAlarmValue

class UpdateAlarmValue(Common):
    """Class for UpdateAlarmValue"""

    def __init__(self):
        """The Constructor for UpdateAlarmValue class"""

        self.postgres = PostgreSQL()
        self.validate_value = ValidateAlarmValue()
        super(UpdateAlarmValue, self).__init__()

    def update_alarm_value(self):
        """
        This API is for Updating Alarm Value
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
          - name: query
            in: body
            description: Updating Alarm Value
            required: true
            schema:
              id: Updating Alarm Value
              properties:
                alarm_value_id:
                    type: string
                name:
                    type: string
                vessel:
                    type: string
                device:
                    type: string
                device_type:
                    type: string
                module:
                    type: string
                option:
                    type: string
                value:
                    type: string
                    example: raw
        responses:
          500:
            description: Error
          200:
            description: Updating Alarm Value
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

        validate = self.validate_value.validate_alarm_value(query_json)

        if validate:

            data['alert'] = validate['alert']
            data['status'] = 'Failed'

            return self.return_data(data)

        if not self.edit_alarm_value(query_json):

            data['alert'] = "Please check your query!"
            data['status'] = 'Failed'
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm value successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def edit_alarm_value(self, query_json):
        """Update Alarm Value"""

        # GET VALUES ALARM VALUE ID
        alarm_value_id = query_json['alarm_value_id']

        # GET CURRENT TIME
        query_json['update_on'] = time.time()

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "alarm_value_id",
            "con": "=",
            "val": alarm_value_id
            })

        # REMOVE KEYS
        query_json = self.remove_key(query_json, "alarm_value_id")

        # UPDATE ALARM VALUE
        if self.postgres.update('alarm_value', query_json, conditions):
            # RETURN
            return 1

        # RETURN
        return 0
