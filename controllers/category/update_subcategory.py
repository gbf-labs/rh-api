"""Update SubCategory"""
import time
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_database import CouchDatabase
from library.couch_queries import Queries


class UpdateSubCategory(Common):
    """Class for UpdateSubCategory"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateSubCategory class"""

        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(UpdateSubCategory, self).__init__()

    def update_subcategory(self):
        """
        This API is for Updating Sub Category
        ---
        tags:
          - Category
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
            description: SubCategory Update
            required: true
            schema:
              id: SubCategory Update
              properties:
                subcategory_id:
                    type: integer
                subcategory_name:
                    type: string
                options:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Update Sub Category
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # UPDATE SUBCATEGORY
        if not self.update(query_json):
            data["alert"] = "Please check your query! | Sub Category Update Failed."
            data['status'] = 'Failed'
            # RETURN ALERT
            return self.return_data(data)

        if query_json['options']:
            if not self.update_subcategory_options(query_json):
                data["alert"] = "Please check your query! | Failed to link options subcategory."
                data['status'] = 'Failed'
                return self.return_data(data)

        data['message'] = "Sub Category successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update(self, query_json):
        """Update SubCategory"""

        query_json['update_on'] = time.time()

        conditions = []

        conditions.append({
            "col": "subcategory_id",
            "con": "=",
            "val": query_json['subcategory_id']
            })

        # data = self.remove_key(query_json, "subcategory_id")
        data = {}
        data['subcategory_name'] = query_json['subcategory_name']

        if self.postgres.update('subcategory', data, conditions):

            return 1

        return 0

    def update_subcategory_options(self, query_json):
        """Update SubCategory Options"""

        subcategory_id = query_json['subcategory_id']
        conditions = []

        conditions.append({
            "col": "subcategory_id",
            "con": "=",
            "val": subcategory_id
        })

        self.postgresql_query.delete('subcategory_options', conditions)

        data = {}
        data['subcategory_id'] = subcategory_id
        for opt in query_json['options']:

            data['option'] = opt
            subcategory = self.postgresql_query.insert('subcategory_options', data,
                                                       str(query_json['subcategory_id']))

            if not subcategory:
                return 0

        return subcategory
