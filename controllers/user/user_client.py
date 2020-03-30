#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=too-many-locals
"""User Client"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UserClient(Common):
    """Class for UserClient"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UserClient class"""
        self.postgres = PostgreSQL()
        super(UserClient, self).__init__()

    # LOGIN FUNCTION
    def user_client(self):
        """
        This API is for Getting all User
        ---
        tags:
          - User
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
            description: User Information
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

        datas = self.get_users(page, limit)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_users(self, page, limit):
        """Return Users"""

        # GET ADMIN ROLE AND SUPER ADMIN ROLE
        sql_str = "SELECT role_id FROM role WHERE role_name in ('admin', 'super admin')"
        l_ids = self.postgres.query_fetch_all(sql_str)
        role_ids = [x['role_id'] for x in l_ids]

        str_ids = ""
        if len(role_ids) == 1:

            str_ids = "(" + str(role_ids[0]) + ")"

        else:

            str_ids = str(tuple(role_ids))

        # CLIENTS
        sql_str = "SELECT * FROM account_role where role_id not in " + str_ids

        client_list = self.postgres.query_fetch_all(sql_str)

        clients = [x['account_id'] for x in client_list]
        clients = set(clients)
        tup_clients = tuple(clients)

        offset = int((page - 1) * limit)

        total_rows = len(tup_clients)

        res = []
        total_page = 0
        if tup_clients:
            # DATA
            sql_str = """
            SELECT a.id, a.username, a.email, a.status,
            a.first_name, a.middle_name, a.last_name, (
            SELECT array_to_json(array_agg(role_perm)) FROM (
            SELECT r.role_id, r.role_name, r.role_details, (
            SELECT array_to_json(array_agg(p)) FROM permission p
            INNER JOIN role_permission rp ON
            rp.permission_id = p.permission_id
            WHERE rp.role_id = r.role_id) AS permissions
            FROM role r INNER JOIN account_role ar
            ON ar.role_id = r.role_id
            WHERE ar.account_id = a.id ) AS role_perm) AS roles, (
            SELECT array_to_json(array_agg(c)) FROM company c
            INNER JOIN account_company ac
            ON ac.company_id = c.company_id
            WHERE ac.account_id = a.id) AS companies FROM account a
            """
            if len(tup_clients) == 1:

                sql_str += " WHERE a.id in ({0})".format(tup_clients[0])
            else:
                sql_str += " WHERE a.id in {0}".format(tup_clients)

            sql_str += " LIMIT {0} OFFSET {1}".format(limit, offset)

            res = self.postgres.query_fetch_all(sql_str)

            # CHECK USERNAME
            if res:
                for result in res:
                    if "no_username" in result['username']:
                        result['username'] = ""

            total_page = int(math.ceil(int(total_rows - 1) / limit)) + 1

        data = {}
        data['rows'] = res
        data['total_rows'] = total_rows
        data['total_page'] = total_page
        data['limit'] = limit
        data['page'] = page

        return data
