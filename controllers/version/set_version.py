# pylint: disable=duplicate-code
"""Set Version"""
import time

from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class SetVersion(Common):
    """Class for SetVersion"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for SetVersion class"""
        self.postgresql_query = PostgreSQL()
        super(SetVersion, self).__init__()

    def set_version(self):
        """
        This API is for Set Version
        ---
        tags:
          - Version
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
            description: Set Version
            required: true
            schema:
              id: Set Version
              properties:
                vessel_id:
                    type: string
                version_id:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Set Version
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
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.insert_vessel_version(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Update vessel version will take at least 30 minutes to take effect!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_vessel_version(self, data):
        """Insert Version"""

        vessel_id = data["vessel_id"]

        sql_str = "SELECT * FROM vessel_version WHERE vessel_id ='{0}'".format(vessel_id)

        ret = self.postgresql_query.query_fetch_one(sql_str)

        if ret:

            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "vessel_id",
                "con": "=",
                "val": vessel_id
                })

            self.postgresql_query.update('vessel_version', data, conditions)

        else:

            vessel_id = self.postgresql_query.insert('vessel_version', data, 'vessel_id')

        if vessel_id:

            data['created_on'] = time.time()

            self.postgresql_query.insert('vessel_version_log', data, 'vessel_id')

            return 1

        return 0
