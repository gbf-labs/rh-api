"""Create Role"""
import time

from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class CreateRole(Common):
    """Class for CreateRole"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateRole class"""
        self.postgres = PostgreSQL()
        super(CreateRole, self).__init__()

    def create_role(self):
        """
        This API is for Creating Role
        ---
        tags:
          - Role
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
            description: Role
            required: true
            schema:
              id: Role
              properties:
                role_name:
                    type: string
                role_details:
                    type: string
                permission_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Role
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

        if not self.insert_role(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Role successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_role(self, query_json):
        """Insert Role"""

        data = {}
        data['role_name'] = query_json['role_name']
        data['role_details'] = query_json['role_details']
        data['created_on'] = time.time()

        role_id = self.postgres.insert('role', data, 'role_id')

        if role_id:

            for permission_id in query_json['permission_ids']:

                temp = {}
                temp['role_id'] = role_id
                temp['permission_id'] = permission_id
                self.postgres.insert('role_permission', temp)

            return 1

        return 0
