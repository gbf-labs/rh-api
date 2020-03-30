"""User Company"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.couch_database import CouchDatabase
from library.couch_queries import Queries

class UserCompany(Common):
    """Class for UserCompany"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UserCompany class"""
        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(UserCompany, self).__init__()

    def user_company(self):
        """
        This API is for Getting User Company
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
          - name: account_id
            in: query
            description: Account ID
            required: true
            type: integer
        responses:
          500:
            description: Error
          200:
            description: User Company
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        account_id = int(request.args.get('account_id'))

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # COMPANY DATA
        datas = self.get_companies(account_id)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_companies(self, account_id):
        """Return Companies"""

        # DATA
        sql_str = "SELECT * FROM account_company WHERE account_id = " + str(account_id)

        res = self.postgresql_query.query_fetch_all(sql_str)

        rows = []

        # COMPANY'S VESSELS-ID
        for company in res:
            company_id = company['company_id']
            vessel_res = self.get_company_vessels(company_id)
            vessels = []
            for vessel in vessel_res['rows']:

                temp = {}
                temp['vessel_id'] = vessel['vessel_id']
                temp['vessel_name'] = self.get_vessel_name(vessel['vessel_id'])
                temp['allow_access'] = self.get_allow_access(account_id, vessel['vessel_id'])
                vessels.append(temp)

            company['vessels'] = vessels
            rows.append(company)

        data = {}
        data['rows'] = rows

        return data

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


    # GET THE VESSEL NAME
    def get_vessel_name(self, vessel_id):
        """Return Vessel Name"""

        values = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )
        if values:
            return values['PARAMETERS']['INFO']['VESSELNAME']
        return ''

    def get_allow_access(self, account_id, vessel_id):
        """Return  Allow access"""

        # DATA
        sql_str = "SELECT * FROM account_vessel"
        sql_str += " WHERE account_id={0} AND vessel_id='{1}'".format(account_id, vessel_id)
        vessel = self.postgres.query_fetch_one(sql_str)

        if vessel:

            return vessel['allow_access']

        return False
