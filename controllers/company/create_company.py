"""Create Company"""
import time
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.log import Log

class CreateCompany(Common):
    """Class for CreateCompany"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateCompany class"""

        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.log = Log()
        super(CreateCompany, self).__init__()

    def create_company(self):
        """
        This API is for Creating Company
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
          - name: query
            in: body
            description: Company
            required: true
            schema:
              id: Company
              properties:
                company_name:
                    type: string
                vessel_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Company
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # EXTRACT QUERY JSON
        company_name = query_json['company_name']
        vessel_ids = query_json['vessel_ids']

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # CREATE COMPANY
        company_id = self.insert_company(company_name)
        if not company_id:
            data["alert"] = "Please check your query! | Company is Already Exist."
            data['status'] = 'Failed'
            # RETURN ALERT
            return self.return_data(data)

        # BIND COMPANY TO VESSELS
        alert, status = self.insert_company_vessels(company_id, vessel_ids)
        if status != 'ok':
            data["alert"] = alert
            data['status'] = status
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Company successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_company(self, company_name):
        """Insert Company"""

        data = {}
        data['company_name'] = company_name
        data['created_on'] = time.time()

        company_id = self.postgresql_query.insert('company', data, 'company_id')

        return company_id or 0

    def insert_company_vessels(self, company_id, vessel_ids):
        """Insert Company Vessels"""

        alert, status = '', ''

        if not self.check_vessel_existence(vessel_ids):
            alert = "Some Vessel/s doesn't exists."
            status = 'Failed'
        else:
            for vessel_id in vessel_ids:
                data = {}
                data['company_id'] = company_id
                data['vessel_id'] = vessel_id
                try:
                    self.postgres.insert('company_vessels', data, 'company_id')
                    alert = ""
                    status = 'ok'

                except TypeError:

                    alert = "ERROR inserting company vessels"
                    status = 'Failed'


        return alert, status

    def check_vessel_existence(self, vessel_ids):
        """Verify if vessel exists"""

        for _id in vessel_ids:
            res = self.couch_query.get_by_id(_id)
            if res.get('error', False):
                return 0

            if res.get('_id', False):
                pass

            else:
                return 0

        return 1
