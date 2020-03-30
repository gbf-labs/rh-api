"""Dashboard"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.couch_database import CouchDatabase
from library.couch_queries import Queries

class Dashboard(Common):
    """Class for Dashboard"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Dashboard class"""
        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(Dashboard, self).__init__()

    def dashboard(self):
        """
        This API is for Getting Dashboard
        ---
        tags:
          - Dashboard
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
            description: Company
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

        # COUNT
        sql_str = "SELECT COUNT(*) FROM company"

        count = self.postgresql_query.query_fetch_one(sql_str)
        total_companies = count['count']

        # GET ALL COMPANIES
        companies = []

        sql_str = "SELECT company_id, company_name FROM company"
        res = self.postgresql_query.query_fetch_all(sql_str)

        # COMPANY'S VESSELS-ID
        for company in res:

            vessel_count = self.get_vessel_count(company['company_id'])

            company['vessels'] = vessel_count
            del company['company_id']
            companies.append(company)

        # COUNT
        sql_str = "SELECT COUNT(*) FROM vessel"

        count = self.postgresql_query.query_fetch_one(sql_str)
        total_vessels = count['count']

        companies = sorted(companies, key=lambda i: i['vessels'])

        companies.reverse()

        data['companies'] = companies

        data['total_companies'] = total_companies
        data['total_vessels'] = total_vessels
        data['status'] = 'ok'
        return self.return_data(data)

    # GET VESSELS OF COMPANY
    def get_vessel_count(self, company_id): #, user=None):
        """Return Company Vessels"""

        assert company_id, "CompanyID is required."

        # DATA
        vessels = []
        sql_str = "SELECT count(*) as vessel FROM company_vessels "
        sql_str += "WHERE company_id={0}".format(company_id)
        vessels = self.postgres.query_fetch_one(sql_str)

        return vessels['vessel']
