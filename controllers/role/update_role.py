"""Update Role"""
import time

from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdateRole(Common):
    """Class for UpdateRole"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateRole class"""
        self.postgres = PostgreSQL()
        super(UpdateRole, self).__init__()

    def update_role(self):
        """
        This API is for Updating Role
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
            description: Updating Role
            required: true
            schema:
              id: Updating Role
              properties:
                role_id:
                    type: string
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
            description: Updating Role
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

        if not self.update_roles(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Role successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_roles(self, query_json):
        """Update Roles"""

        # GET CURRENT TIME
        query_json['update_on'] = time.time()

        # GET VALUES ROLE AND PERMISSION
        role_id = query_json['role_id']
        permission_ids = query_json['permission_ids']

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "role_id",
            "con": "=",
            "val": role_id
            })

        # REMOVE KEYS
        query_json = self.remove_key(query_json, "role_id")
        query_json = self.remove_key(query_json, "permission_ids")

        # UPDATE ROLE
        if self.postgres.update('role', query_json, conditions):

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "role_id",
                "con": "=",
                "val": role_id
                })

            # DELETE OLD PERMISSION
            self.postgres.delete('role_permission', conditions)

            # LOOP NEW PERMISSIONS
            for permission_id in permission_ids:

                # INIT NEW PERMISSION
                temp = {}
                temp['role_id'] = role_id
                temp['permission_id'] = permission_id

                # INSERT NEW PERMISSION OF ROLE
                self.postgres.insert('role_permission', temp)

            # RETURN
            return 1

        # RETURN
        return 0
