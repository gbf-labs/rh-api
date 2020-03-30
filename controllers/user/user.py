#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=too-many-arguments, too-many-statements, too-many-locals, too-many-branches
"""User"""
import math
from configparser import ConfigParser
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class User(Common):
    """Class for User"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for User class"""
        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(User, self).__init__()

    # LOGIN FUNCTION
    def user(self):
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
          - name: sort_type
            in: query
            description: Sort Type
            required: false
            type: string
          - name: sort_column
            in: query
            description: Sort Column
            required: false
            type: string
          - name: filter_column
            in: query
            description: Filter Column
            required: false
            type: string
          - name: filter_value
            in: query
            description: Filter Value
            required: false
            type: string
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
        sort_type = request.args.get('sort_type')
        sort_column = request.args.get('sort_column')
        filter_column = request.args.get('filter_column')
        filter_value = request.args.get('filter_value')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if filter_column and filter_value:

            filter_list = []
            for col in filter_column.split(","):
                filter_list.append(col)

            filter_val = []
            for val in filter_value.split(","):
                filter_val.append(val)

            filter_value = tuple(filter_val)

        else:

            filter_list = filter_column

        datas = self.get_users(page, limit, sort_type, sort_column,
                               filter_list, filter_value)

        keys = ['username', 'email', 'status']

        for key in keys:

            user_data = self.get_account_data(key)
            format_data = self.data_filter(user_data, key)

            if key == "username":
                usernames = format_data

            if key == "email":
                emails = format_data

            if key == "status":
                status = format_data

        datas['username'] = usernames
        datas['email'] = emails
        datas['status2'] = status
        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_users(self, page, limit, sort_type, sort_column,
                  filter_list, filter_value):
        """Return Users"""

        offset = int((page - 1) * limit)

        sql_str = " SELECT a.id, a.username, a.email, a.status,"
        sql_str += " a.first_name, a.middle_name, a.last_name,"
        sql_str += " (SELECT array_to_json(array_agg(role_perm))"
        sql_str += " FROM (SELECT r.role_id, r.role_name, r.role_details, "
        sql_str += " (SELECT array_to_json(array_agg(p)) FROM permission p "
        sql_str += " INNER JOIN role_permission rp ON rp.permission_id = p.permission_id "
        sql_str += " WHERE rp.role_id = r.role_id) AS permissions FROM role r"
        sql_str += " INNER JOIN account_role ar ON ar.role_id = r.role_id"
        sql_str += " WHERE ar.account_id = a.id) AS role_perm) AS roles,"
        sql_str += " (SELECT array_to_json(array_agg(c)) FROM company c"
        sql_str += " INNER JOIN account_company ac ON ac.company_id = c.company_id"
        sql_str += " WHERE ac.account_id = a.id) AS companies FROM account a"

        #WHERE STATEMENT
        where_sql = ""

        if filter_list and filter_value:

            where = []

            i = 0
            for val in filter_value:

                key = filter_list[i]

                if key in ['roles', 'role', 'role_name']:
                    where_st = """a.id in (SELECT account_id FROM role r
                        LEFT JOIN account_role ar ON r.role_id = ar.role_id
                        WHERE r.role_name ILIKE '{0}')""".format(val)

                elif key in ['companies', 'company', 'company_name']:
                    where_st = """a.id in (SELECT account_id FROM company c
                            LEFT JOIN account_company ac ON c.company_id = ac.company_id
                            WHERE c.company_name ILIKE '{0}')""".format(val)

                elif key == "status":
                    status = bool(val == "Enabled")
                    # if val == "Enabled":
                    #     status = True
                    # else:
                    #     status = False
                    where_st = "a.status = '{0}'".format(status)

                else:
                    where_st = "a.{0} ILIKE '{1}'".format(key, val)

                i += 1

                where.append(where_st)

            where_sql = " AND ".join(where)


        if where_sql:
            sql_str += " WHERE {0}".format(where_sql)

        #SORT
        if sort_column and sort_type:

            if sort_column in ['username', 'email', 'status']:
                table = "a.{0}".format(sort_column)
                sql_str += " ORDER BY  {0} {1}".format(table, sort_type.lower())

        else:
            sql_str += " ORDER BY a.created_on desc"

        # COUNT
        count_str = "SELECT COUNT(*) FROM ({0}) as accounts".format(sql_str)
        count = self.postgres.query_fetch_one(count_str)

        #LIMIT
        sql_str += " LIMIT {0} OFFSET {1}".format(limit, offset)

        accounts = self.postgres.query_fetch_all(sql_str)

        # CHECK USERNAME
        if accounts:
            for account in accounts:
                if "no_username" in account['username']:
                    account['username'] = ""

        total_rows = count['count']
        total_page = int(math.ceil(int(total_rows - 1) / limit)) + 1

        rows = []

        if self.vpn_db_build.upper() == 'TRUE':

            for account in accounts:
                account_id = account['id']

                sql_str = "SELECT * FROM job WHERE job_id in ("
                sql_str += "SELECT job_id FROM account_vpn WHERE "
                sql_str += "account_id={0} and status=true)".format(account_id)

                jobs = self.postgres.query_fetch_all(sql_str)

                account['vessel_vpn'] = ""
                account['web_vpn'] = ""

                for job in jobs:

                    if job['vpn_type'] in ['VCLIENT', 'VRH']:

                        filename = job['directory'].split("/")[-1]
                        account['vessel_vpn'] = "download/vpn/{0}".format(filename)

                    elif job['vpn_type'] in ['CLIENT', 'RHADMIN']:

                        filename = job['directory'].split("/")[-1]
                        account['web_vpn'] = "download/vpn/{0}".format(filename)

                rows.append(account)

        else:

            rows = accounts

        data = {}
        data['rows'] = rows
        data['total_rows'] = total_rows
        data['total_page'] = total_page
        data['limit'] = limit
        data['page'] = page

        return data


    def get_account_data(self, key):
        """Return Account Data"""

        if key:

            # DATA
            sql_str = "SELECT DISTINCT {0} FROM account".format(key)

            datas = self.postgres.query_fetch_all(sql_str)

            data = {}

            k = "{0}s".format(key)

            temp_data = [temp_data[key] for temp_data in datas]

            data[k] = temp_data

        return data
