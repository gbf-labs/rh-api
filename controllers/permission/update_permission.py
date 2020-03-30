"""Update Permission"""
import time

from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdatePermission(Common):
    """Class for UpdatePermission"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdatePermission class"""
        self.postgresql_query = PostgreSQL()
        super(UpdatePermission, self).__init__()

    def update_permission(self):
        """
        This API is for Updating permission
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
            description: Updating Permission
            required: true
            schema:
              id: Updating Permission
              properties:
                permission_id:
                    type: string
                permission_name:
                    type: string
                permission_details:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Updating Permission
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

        if not self.update_permissions(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Permission successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_permissions(self, query_json):
        """Update Permission"""
        query_json['update_on'] = time.time()

        conditions = []

        conditions.append({
            "col": "permission_id",
            "con": "=",
            "val": query_json['permission_id']
            })

        data = self.remove_key(query_json, "permission_id")

        if self.postgresql_query.update('permission', data, conditions):

            return 1

        return 0
