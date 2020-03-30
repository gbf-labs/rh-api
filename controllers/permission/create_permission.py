# pylint: disable=duplicate-code
"""Create Permission"""
import time

from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class CreatePermission(Common):
    """Class for CreatePermission"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreatePermission class"""
        self.postgresql_query = PostgreSQL()
        super(CreatePermission, self).__init__()

    def create_permission(self):
        """
        This API is for Creating Permission
        ---
        tags:
          - Permission
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
            description: Permission
            required: true
            schema:
              id: Permission
              properties:
                permission_name:
                    type: string
                permission_details:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Permission
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        permission_name = query_json["permission_name"]
        permission_details = query_json["permission_details"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.insert_permissions(permission_name, permission_details):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Permission successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_permissions(self, permission_name, permission_details):
        """Insert Permissions"""

        data = {}
        data['permission_name'] = permission_name
        data['permission_details'] = permission_details
        data['created_on'] = time.time()

        if self.postgresql_query.insert('permission', data, 'permission_id'):

            return 1

        return 0
