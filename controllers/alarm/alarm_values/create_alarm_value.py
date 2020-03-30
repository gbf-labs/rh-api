"""Create Alarm Value"""
import time
from flask import request
from library.common import Common
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL
from controllers.alarm.alarm_values.validate_alarm_value import ValidateAlarmValue

class CreateAlarmValue(Common):
    """Class for CreateAlarmValue"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateAlarmValue class"""

        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.validate_value = ValidateAlarmValue()
        super(CreateAlarmValue, self).__init__()

    def create_alarm_value(self):
        """
        This API is for Creating Alarm Values
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
            description: Alarm Value
            required: true
            schema:
              id: AlarmValue
              properties:
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
            description: Alarm Value
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

        if not self.insert_alarm_value(query_json):

            data['alert'] = "Please check your query! | Alarm Value is Already Exist."
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm value successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_alarm_value(self, query_json):
        """Insert Alarm Value"""

        query_json['created_on'] = time.time()

        if self.postgres.insert('alarm_value', query_json, 'alarm_value_id'):
            return 1

        return 0
