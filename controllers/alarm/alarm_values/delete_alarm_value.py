"""Delete Alarm Value"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteAlarmValue(Common):
    """Class for DeleteAlarmValue"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteAlarmValue class"""

        self.postgres = PostgreSQL()
        super(DeleteAlarmValue, self).__init__()

    def delete_alarm_value(self):
        """
        This API is for Deleting Alarm Value
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
            description: Alarm Value IDs
            required: true
            schema:
              id: Delete Alarm Values
              properties:
                alarm_value_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Alarm Value
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        alarm_value_ids = query_json["alarm_value_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_alarm_values(alarm_value_ids):
            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            self.postgres.close_connection()
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Alarm value successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_alarm_values(self, alarm_value_ids):
        """Delete Alarm Values"""

        conditions = []

        conditions.append({
            "col": "alarm_value_id",
            "con": "in",
            "val": alarm_value_ids
            })

        if self.postgres.delete('alarm_value', conditions):
            return 1

        return 0
