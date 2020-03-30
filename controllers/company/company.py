# pylint: disable=too-many-locals
"""Company"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.couch_database import CouchDatabase
from library.couch_queries import Queries

class Company(Common):
    """Class for Company"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Company class"""
        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(Company, self).__init__()

    def company(self):
        """
        This API is for Getting Company
        ---
        tags:
          - Company
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
            description: Company
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

        # COMPANY DATA
        datas = self.get_companies(page, limit)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_companies(self, page, limit):
        """Return List of Companies"""

        offset = int((page - 1) * limit)

        # COUNT
        sql_str = "SELECT COUNT(*) FROM company"

        count = self.postgresql_query.query_fetch_one(sql_str)
        total_rows = count['count']

        # DATA
        sql_str = "SELECT * FROM company ORDER BY company_name ASC"
        sql_str += " LIMIT {0} OFFSET {1} ".format(limit, offset)

        res = self.postgresql_query.query_fetch_all(sql_str)

        rows = []

        # COMPANY'S VESSELS-ID
        for company in res:
            company_id = company['company_id']
            vessel_res = self.get_company_vessels(company_id)
            vessels = []
            for vessel in vessel_res['rows']:
                allow_access = False
                temp = {}
                temp['vessel_id'] = vessel['vessel_id']
                temp['vessel_name'] = self.get_vessel_name(vessel['vessel_id'])
                temp['allow_access'] = allow_access
                vessels.append(temp)

            company['vessels'] = vessels
            rows.append(company)

        total_page = int(math.ceil(int(total_rows - 1) / limit)) + 1

        data = {}
        data['rows'] = rows
        data['total_rows'] = total_rows
        data['total_page'] = total_page
        data['limit'] = limit
        data['page'] = page

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
