"""Delete Alarm Condition"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteAlarmCondition(Common):
    """Class for DeleteAlarmCondition"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteAlarmCondition class"""

        self.postgres = PostgreSQL()
        super(DeleteAlarmCondition, self).__init__()

    def delete_alarm_condition(self):
        """
        This API is for Deleting Alarm Condition
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
            description: Alarm Condition IDs
            required: true
            schema:
              id: Delete Alarm Condition
              properties:
                alarm_condition_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Alarm Condition
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        alarm_condition_ids = query_json["alarm_condition_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_alarm_conditions(alarm_condition_ids):
            data['alert'] = "Please check your query!"
            data['status'] = 'Failed'

            self.postgres.close_connection()
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm condition successfully Deleted!"
        data['status'] = "ok"

        return self.return_data(data)

    def delete_alarm_conditions(self, alarm_condition_ids):
        """Delete Alarm Conditions"""

        conditions = []

        conditions.append({
            "col": "alarm_condition_id",
            "con": "in",
            "val": alarm_condition_ids
            })

        if self.postgres.delete('alarm_condition', conditions):
            return 1

        return 0
