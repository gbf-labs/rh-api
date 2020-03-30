"""Update Alarm Trigger"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdateAlarmTrigger(Common):
    """Class for UpdateAlarmTrigger"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateAlarmTrigger class"""

        self.postgres = PostgreSQL()
        super(UpdateAlarmTrigger, self).__init__()

    def update_alarm_trigger(self):
        """
        This API is for Updating Alarm Trigger
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
            description: Updating Alarm Trigger
            required: true
            schema:
              id: Updating Alarm Trigger
              properties:
                alarm_trigger_id:
                    type: string
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
            description: Updating Alarm Trigger
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

        if not query_json:

            data['alert'] = "Field/s cannot be empty!"
            data['status'] = 'Failed'

            return self.return_data(data)

        if not self.edit_alarm_trigger(query_json):

            data['alert'] = "Please check your query!"
            data['status'] = 'Failed'
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm Trigger successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def edit_alarm_trigger(self, query_json):
        """Update Alarm Trigger"""

        # GET ALARM TRIGGER ID
        alarm_trigger_id = query_json['alarm_trigger_id']

        # GET CURRENT TIME
        query_json['update_on'] = time.time()

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "alarm_trigger_id",
            "con": "=",
            "val": alarm_trigger_id
            })

        # REMOVE KEYS
        query_json = self.remove_key(query_json, "alarm_trigger_id")

        # UPDATE ALARM TRIGGER
        if self.postgres.update('alarm_trigger', query_json, conditions):
            # RETURN
            return 1

        # RETURN
        return 0
