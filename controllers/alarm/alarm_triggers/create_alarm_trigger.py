"""Create Alarm Trigger"""
import time
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class CreateAlarmTrigger(Common):
    """Class for CreateAlarmTrigger"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateAlarmTrigger class"""

        self.postgres = PostgreSQL()
        super(CreateAlarmTrigger, self).__init__()

    def create_alarm_trigger(self):
        """
        This API is for Creating Alarm Trigger
        ---
        tags:
          - Alarm Triggers
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
            description: Alarm Trigger
            required: true
            schema:
              id: AlarmTrigger
              properties:
                alarm_type_id:
                    type: integer
                alarm_condition_id:
                    type: integer
                alarm_enabled:
                    type: string
                    example: True/False
                alarm_email:
                    type: string
                    example: True/False
                email:
                    type: string
                label:
                    type: string
                description:
                    type: string
                is_acknowledged:
                    type: string
                    example: True/False
        responses:
          500:
            description: Error
          200:
            description: Alarm Trigger
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

            return self.return_data(data)

        if not query_json:

            data['alert'] = "Field/s cannot be empty!"
            data['status'] = 'Failed'

            return self.return_data(data)

        if not self.insert_alarm_trigger(query_json):

            data['alert'] = "Please check your query! | Alarm Trigger is Already Exist."
            data['status'] = 'Failed'

            return self.return_data(data)

        data['message'] = "Alarm trigger successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_alarm_trigger(self, query_json):
        """Insert Alarm Trigger"""

        query_json['created_on'] = time.time()

        self.postgres.insert('alarm_trigger', query_json, 'alarm_trigger_id')

        return 1
