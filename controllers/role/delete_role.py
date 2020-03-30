"""Delete Role"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteRole(Common):
    """Class for DeleteRole"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteRole class"""
        self.postgres = PostgreSQL()
        super(DeleteRole, self).__init__()

    def delete_role(self):
        """
        This API is for Deleting Role
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
            description: Role IDs
            required: true
            schema:
              id: Delete Roles
              properties:
                role_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Role
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        role_ids = query_json["role_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.can_delete(role_ids):

            data["alert"] = "Can't delete default role!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_roles(role_ids):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Role successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_roles(self, role_ids):
        """Delete Roles"""
        conditions = []

        conditions.append({
            "col": "role_id",
            "con": "in",
            "val": role_ids
            })

        if self.postgres.delete('role', conditions):

            return 1

        return 0

    def can_delete(self, role_ids):
        """Check if can delete roles"""

        # DATA
        sql_str = "SELECT role_id FROM role WHERE default_value=TRUE"
        def_role = self.postgres.query_fetch_all(sql_str)
        def_role = {x['role_id'] for x in def_role}

        role_ids = set(role_ids)

        if def_role.isdisjoint(role_ids):
            return 1

        return 0
