# pylint: disable=broad-except
"""Update Company"""
import time

from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.log import Log

class UpdateCompany(Common):
    """Class for UpdateCompany"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateCompany class"""
        self.postgres = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.log = Log()
        super(UpdateCompany, self).__init__()

    def update_company(self):
        """
        This API is for Updating Company
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
            description: Updating Company
            required: true
            schema:
              id: Updating Company
              properties:
                company_id:
                    type: string
                company_name:
                    type: string
                vessel_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Updating Company
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET COMPANY_ID
        company_id = query_json.get('company_id')
        vessel_ids = query_json.get('vessel_ids')
        del query_json['vessel_ids']

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        vessel_ids = self.check_vessel_existence(vessel_ids)

        if not self.update_companies(query_json):
            data["alert"] = "Please check your query! , Company update FAILED."
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # GET CURRENT VESSELS ID
        # current_vessels = self.get_current_vessels(company_id)

        # removed_vessel, added_vessel = self.set_vessels_data(current_vessels, vessel_ids)

        self.get_users(company_id)

        # self.update_users_vessel(user_ids, removed_vessel, added_vessel)

        # DELETE CURRENT VESSELS
        if not self.delete_current_vessels(company_id):
            data["alert"] = "Problem in updating the vessels."
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if len(vessel_ids) > 0:
            #INSERT NEW VESSELS
            if not self.add_vessels(company_id, vessel_ids):
                data["alert"] = "Problem in updating the vessels."
                data['status'] = "Failed"
                # RETURN ALERT
                return self.return_data(data)

        data['message'] = "Company successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_companies(self, query_json):
        """Update Companies"""

        query_json['update_on'] = time.time()

        conditions = []

        conditions.append({
            "col": "company_id",
            "con": "=",
            "val": query_json['company_id']
            })

        data = self.remove_key(query_json, "company_id")

        if self.postgres.update('company', data, conditions):

            return 1

        return 0

    def check_vessel_existence(self, vessel_ids):
        """Check Vessel Existence"""

        ids = []

        for _id in vessel_ids:

            res = self.couch_query.get_by_id(_id)
            if res.get('_id', False):
                ids.append(_id)

        return ids

    def delete_current_vessels(self, company_id):
        """Delete Current Vessels"""

        status = False
        try:
            conditions = []

            conditions.append({
                "col": "company_id",
                "con": "=",
                "val": company_id
                })

            if self.postgres.delete('company_vessels', conditions):
                status = True

        except Exception as error:
            self.log.critical(error)
            status = False

        return status

    def add_vessels(self, company_id, vessel_ids):
        """Add Vessels"""

        status = ''

        for vessel_id in vessel_ids:
            data = {}
            data['company_id'] = company_id
            data['vessel_id'] = vessel_id
            try:
                self.postgres.insert('company_vessels', data, 'company_id')
                status = 'ok'
            except Exception as err:
                self.log.critical(err)
                status = 'Failed'


        return status

    # def get_current_vessels(self, company_id):

    #     sql_str = "SELECT * FROM company_vessels"
    #     sql_str += " WHERE company_id={0}".format(company_id)
    #     rows = self.postgres.query_fetch_all(sql_str)


    #     if rows:

    #         return [x['vessel_id'] for x in rows]

    #     return []

    # def set_vessels_data(self, current_vessels, vessel_ids):

    #     current_vessels = set(current_vessels)
    #     vessel_ids = set(vessel_ids)

    #     rep_current_vessels = current_vessels.copy()
    #     rep_vessel_ids = vessel_ids.copy()

    #     rep_vessel_ids.difference_update(current_vessels)
    #     rep_current_vessels.difference_update(vessel_ids)

    #     return [rep_current_vessels, rep_vessel_ids]

    def get_users(self, company_id):
        """Get Users"""

        sql_str = "SELECT * FROM account_company WHERE company_id={0}".format(company_id)
        rows = self.postgres.query_fetch_all(sql_str)

        if rows:

            for row in rows:

                # INIT CONDITION
                conditions = []

                # CONDITION FOR QUERY
                conditions.append({
                    "col": "id",
                    "con": "=",
                    "val": row['account_id']
                    })

                updates = {}
                updates['vessel_vpn_state'] = 'pending'

                # UPDATE VESSEL VPN STATE
                self.postgres.update('account', updates, conditions)

            return [x['account_id'] for x in rows]

        return []

    # def update_users_vessel(self, user_ids, removed_vessel, added_vessel):

    #     users_vessel = []
    #     for user_id in user_ids:

    #         sql_str = "SELECT * FROM account_company WHERE account_id = " + str(user_id)

    #         res = self.postgres.query_fetch_all(sql_str)

    #         users = []

    #         # COMPANY'S VESSELS-ID
    #         for company in res:
    #             company_id = company['company_id']
    #             vessel_res = self.get_company_vessels(company_id)
    #             vessels = []
    #             for vessel in vessel_res['rows']:

    #                 temp = {}
    #                 temp['vessel_id'] = vessel['vessel_id']
    #                 temp['allow_access'] = self.get_allow_access(user_id, vessel['vessel_id'])
    #                 vessels.append(temp)

    #             company['vessels'] = vessels
    #             users.append(company)

    #         data = self.set_user_data(users)
    #         users_vessel.append(data)

    #     print("users_vessel: ", users_vessel)

    #     return users_vessel

    # GET VESSELS OF COMPANY
    # def get_company_vessels(self, company_id): #, user=None):

    #     assert company_id, "CompanyID is required."

    #     # DATA
    #     vessels = []
    #     sql_str = "SELECT * FROM company_vessels WHERE company_id={0}".format(company_id)
    #     vessels = self.postgres.query_fetch_all(sql_str)

    #     data = {}
    #     data['rows'] = vessels

    #     return data

    # def get_allow_access(self, account_id, vessel_id):

    #     # DATA
    #     sql_str = "SELECT * FROM account_vessel WHERE account_id={0}".format(account_id)
    #     sql_str += " AND vessel_id='{0}'".format(vessel_id)
    #     vessel = self.postgres.query_fetch_one(sql_str)

    #     if vessel:

    #         return vessel['allow_access']

    #     return False

    # def set_user_data(self, datas):

    #     result = []
    #     vessels = []
    #     for data in datas:

    #         for vessel in data['vessels']:
    #             if vessel['vessel_id'] not in vessels:

    #                 vessels.append(vessel['vessel_id'])
    #                 vessel['account_id'] = data['account_id']
    #                 result.append(vessel)

    #     return result
