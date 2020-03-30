# pylint: disable=duplicate-code
"""Create Version"""
import time

from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class CreateVersion(Common):
    """Class for CreateVersion"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateVersion class"""
        self.postgresql_query = PostgreSQL()
        super(CreateVersion, self).__init__()

    def create_version(self):
        """
        This API is for Creating Version
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
            description: Version
            required: true
            schema:
              id: Version
              properties:
                version_name:
                    type: string
                web:
                    type: string
                api:
                    type: string
                backend:
                    type: string
                description:
                    type: string
                status:
                    type: boolean
                latest:
                    type: boolean
        responses:
          500:
            description: Error
          200:
            description: Version
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

        sql_str = "SELECT * FROM version WHERE version_name="
        sql_str += "'{0}'".format(query_json["version_name"])

        ver = self.postgresql_query.query_fetch_one(sql_str)

        if ver:

            data["alert"] = "Version name already exist!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.insert_version(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Version successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_version(self, data):
        """Insert Version"""

        latest = data["latest"]

        data = self.remove_key(data, "latest")

        if data["status"] in ["null", "", "NaN"]:
            data["status"] = True

        data['created_on'] = time.time()

        version_id = self.postgresql_query.insert('version', data, 'version_id')

        if version_id:

            if latest:

                lv_data = {}
                lv_data["version_id"] = version_id

                sql_str = "SELECT * FROM latest_version"

                ret = self.postgresql_query.query_fetch_one(sql_str)

                if ret:

                    conditions = []

                    # CONDITION FOR QUERY
                    conditions.append({
                        "col": "latest_version_id",
                        "con": "=",
                        "val": True
                        })

                    self.postgresql_query.update('latest_version', lv_data, conditions)

                else:

                    self.postgresql_query.insert('latest_version', lv_data)


            return 1

        return 0
