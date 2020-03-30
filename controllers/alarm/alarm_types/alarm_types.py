"""Alarm Types"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class AlarmTypes(Common):
    """Class for AlarmTypes"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmTypes class"""

        self.postgres = PostgreSQL()
        super(AlarmTypes, self).__init__()

    def alarm_types(self):
        """
        This API is for Getting Alarm Type
        ---
        tags:
          - Alarm Types
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
            description: Alarm Type
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['data'] = []

        #GET DATA
        datas = self.get_alarm_types()

        if datas:
            rows = datas['rows']

        else:
            rows = []

        final_data = rows
        total_count = len(final_data)
        data['data'] = final_data
        data['total_rows'] = total_count
        data['status'] = 'ok'

        return self.return_data(data)

    def get_alarm_types(self):
        """Get Alarm Types"""

        # DATA
        sql_str = "SELECT * FROM alarm_type"

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        return data
