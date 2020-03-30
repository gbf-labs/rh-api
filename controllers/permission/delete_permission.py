"""Delete Permission"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeletePermission(Common):
    """Class for DeletePermission"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeletePermission class"""
        self.postgresql_query = PostgreSQL()
        super(DeletePermission, self).__init__()

    def delete_permission(self):
        """
        This API is for Deleting Permission
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
            description: Permission IDs
            required: true
            schema:
              id: Delete Permissions
              properties:
                permission_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Permission
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        permission_ids = query_json["permission_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.can_delete(permission_ids):

            data["alert"] = "Can't delete default permission!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_permissions(permission_ids):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Permission successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_permissions(self, permission_ids):
        """Delete Permissions"""

        conditions = []

        conditions.append({
            "col": "permission_id",
            "con": "in",
            "val": permission_ids
            })

        if self.postgresql_query.delete('permission', conditions):

            return 1

        return 0

    def can_delete(self, permission_ids):
        """Check if can delete permissions"""

        # DATA
        sql_str = "SELECT permission_id FROM permission WHERE default_value=TRUE"
        def_perm = self.postgres.query_fetch_all(sql_str)
        def_perm = {x['permission_id'] for x in def_perm}

        permission_ids = set(permission_ids)

        if def_perm.isdisjoint(permission_ids):
            return 1

        return 0
