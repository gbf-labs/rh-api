"""Noon Report"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

# from library.couch_database import CouchDatabase
# from library.couch_queries import Queries

class NoonReport(Common):
    """Class for NoonReport"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for NoonReport class"""
        self.postgresql_query = PostgreSQL()
        super(NoonReport, self).__init__()

    def noon_report(self):
        """
        This API is to get noon report
        ---
        tags:
          - Email
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
          - name: vessel_id
            in: query
            description: Vessel ID
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
        vessel_id = request.args.get('vessel_id')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # COMPANY DATA
        datas = self.get_noon_report(vessel_id, page, limit)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_noon_report(self, vessel_id, page, limit):
        """Return Noon Report"""

        offset = int((page - 1) * limit)

        # COUNT
        sql_str = "SELECT COUNT(*) "
        sql_str += " FROM email_log el INNER JOIN email_vessel ev ON"
        sql_str += " el.email_vessel_id=ev.email_vessel_id WHERE"
        sql_str += " ev.vessel_id='" + vessel_id + "'"

        count = self.postgresql_query.query_fetch_one(sql_str)
        total_rows = count['count']

        # DATA
        sql_str = "SELECT el.mail_log_id, el.created_on, ev.email"
        sql_str += " FROM email_log el INNER JOIN email_vessel ev ON"
        sql_str += " el.email_vessel_id=ev.email_vessel_id WHERE"
        sql_str += " ev.vessel_id='{0}' LIMIT {1} OFFSET {2} ".format(vessel_id, limit, offset)

        rows = self.postgresql_query.query_fetch_all(sql_str)

        total_page = int(math.ceil(int(total_rows - 1) / limit))

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
