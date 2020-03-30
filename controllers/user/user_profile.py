#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
"""User Profile"""
from flask import  request
from library.common import Common
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL

class UserProfile(Common):
    """Class for """

    # INITIALIZE
    def __init__(self):
        """The Constructor for UserProfile class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(UserProfile, self).__init__()

    # LOGIN FUNCTION
    def user_profile(self):
        """
        This API is for Getting User Information
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

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # OPEN CONNECTION
        self.postgres.connection()

        datas = self.get_users(userid)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_users(self, userid):
        """Return Users"""

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
        WHERE ar.account_id = a.id) AS role_perm) AS roles, (
        SELECT array_to_json(array_agg(c)) FROM company c
        INNER JOIN account_company ac
        ON ac.company_id = c.company_id
        WHERE ac.account_id = a.id) AS companies FROM account a 
        WHERE a.id=
        """
        sql_str += userid

        res = self.postgres.query_fetch_one(sql_str)

        if res:
            if "no_username" in res['username']:
                res['username'] = ""

        res["vessels"] = self.get_vessels(userid)

        data = {}
        data['data'] = res

        return data

    def get_vessels(self, account_id):
        """Return Companies"""

        # DATA
        sql_str = "SELECT * FROM account_company WHERE account_id = " + str(account_id)

        res = self.postgres.query_fetch_all(sql_str)

        vessels = []

        # COMPANY'S VESSELS-ID
        for company in res:
            company_id = company['company_id']
            vessel_res = self.get_company_vessels(company_id)
            for vessel in vessel_res['rows']:

                temp = {}
                temp['vessel_id'] = vessel['vessel_id']
                temp['allow_access'] = self.get_allow_access(account_id, vessel['vessel_id'])
                vessels.append(temp)

        return vessels

    # GET VESSELS OF COMPANY
    def get_company_vessels(self, company_id): #, user=None):
        """Return Company Vessels"""

        assert company_id, "CompanyID is required."

        # DATA
        vessels = []
        sql_str = "SELECT * FROM company_vessels WHERE company_id={0}".format(company_id)
        vessels = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = vessels

        return data

    def get_allow_access(self, account_id, vessel_id):
        """Return  Allow access"""

        # DATA
        sql_str = "SELECT * FROM account_vessel"
        sql_str += " WHERE account_id={0} AND vessel_id='{1}'".format(account_id, vessel_id)
        vessel = self.postgres.query_fetch_one(sql_str)

        if vessel:

            return vessel['allow_access']

        return False
