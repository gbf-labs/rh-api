"""Permission"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class Permission(Common):
    """Class for Permission"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Permission class"""
        self.postgresql_query = PostgreSQL()
        super(Permission, self).__init__()

    def permission(self):
        """
        This API is for Getting Permission
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
          - name: limit
            in: query
            description: Limit
            required: true
            type: integer
          - name: page
            in: query
            description: Page
            required: true
            type: integer
        responses:
          500:
            description: Error
          200:
            description: Permission
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        page = int(request.args.get('page'))
        limit = int(request.args.get('limit'))

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        datas = self.get_permissions(page, limit)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_permissions(self, page, limit):
        """Return Permissions"""
        offset = int((page - 1) * limit)

        # COUNT
        sql_str = "SELECT COUNT(*) FROM permission"

        count = self.postgresql_query.query_fetch_one(sql_str)
        total_rows = count['count']

        # DATA
        sql_str = "SELECT * FROM permission LIMIT {0} OFFSET {1} ".format(limit, offset)

        res = self.postgresql_query.query_fetch_all(sql_str)

        total_page = int(math.ceil(int(total_rows - 1) / limit)) + 1

        data = {}
        data['rows'] = res
        data['total_rows'] = total_rows
        data['total_page'] = total_page
        data['limit'] = limit
        data['page'] = page

        return data
