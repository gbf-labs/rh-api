"""Delete Company"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteCompany(Common):
    """Class for DeleteCompany"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteCompany class"""
        self.postgresql_query = PostgreSQL()
        super(DeleteCompany, self).__init__()

    def delete_company(self):
        """
        This API is for Deleting Company
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
            description: Company IDs
            required: true
            schema:
              id: Delete Companies
              properties:
                company_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Company
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        company_ids = query_json["company_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.can_delete(company_ids):

            data["alert"] = "Can't delete default company!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_companies(company_ids):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Company successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_companies(self, company_ids):
        """Delete Companies"""

        conditions = []

        conditions.append({
            "col": "company_id",
            "con": "in",
            "val": company_ids
            })

        if self.postgresql_query.delete('account_company', conditions):

            conditions = []

            conditions.append({
                "col": "company_id",
                "con": "in",
                "val": company_ids
                })

            if self.postgresql_query.delete('company', conditions):

                return 1

        return 0

    def can_delete(self, company_ids):
        """Check Company if can be deleted"""

        # DATA
        sql_str = "SELECT company_id FROM company WHERE default_value=TRUE"
        def_comp = self.postgres.query_fetch_all(sql_str)
        def_comp = {x['company_id'] for x in def_comp}

        company_ids = set(company_ids)

        if def_comp.isdisjoint(company_ids):
            return 1

        return 0
