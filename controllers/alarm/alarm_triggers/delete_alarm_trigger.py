"""Delete Alarm Trigger"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteAlarmTrigger(Common):
    """Class for DeleteAlarmTrigger"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteAlarmTrigger class"""
        self.postgres = PostgreSQL()
        super(DeleteAlarmTrigger, self).__init__()

    def delete_alarm_trigger(self):
        """
        This API is for Deleting Alarm Trigger
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
            description: Alarm Trigger IDs
            required: true
            schema:
              id: Delete Alarm Triggers
              properties:
                alarm_trigger_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Alarm Trigger
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        alarm_trigger_ids = query_json["alarm_trigger_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_alarm_triggers(alarm_trigger_ids):
            data['alert'] = "Please check your query!"
            data['status'] = 'Failed'

            self.postgres.close_connection()
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm trigger successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_alarm_triggers(self, alarm_trigger_ids):
        """Delete Alarm Triggers"""

        conditions = []

        conditions.append({
            "col": "alarm_trigger_id",
            "con": "in",
            "val": alarm_trigger_ids
            })

        if self.postgres.delete('alarm_trigger', conditions):
            return 1

        return 0
