"""Create SubCategory"""
import time
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_database import CouchDatabase
from library.couch_queries import Queries


class CreateSubCategory(Common):
    """Class for CreateSubCategory"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CreateSubCategory class"""

        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(CreateSubCategory, self).__init__()

    def create_subcategory(self):
        """
        This API is for Creating Sub Category
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
            description: SubCategory
            required: true
            schema:
              id: SubCategory
              properties:
                subcategory_name:
                    type: string
                options:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Create Sub Category
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # EXTRACT QUERY JSON
        subcategory_name = query_json['subcategory_name']
        options = query_json['options']

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # CREATE SUBCATEGORY
        subcategory_id = self.insert_subcategory(subcategory_name)

        if not subcategory_id:
            data["alert"] = "Please check your query! | Sub Category is already exist."
            data['status'] = 'Failed'
            return self.return_data(data)

        # LINK OPTIONS TO SUBCATEGORY
        if options:
            if not self.insert_subcategory_options(subcategory_id, options):
                # DELETE NEWLY CREATED SUBCATEGORY BECAUSE OF CONFLICT ON UI / UX
                self.delete_subcategory(subcategory_id)

                data["alert"] = "Failed to Link Options to Sub Category."
                data['status'] = 'Failed'
                return self.return_data(data)

        data['message'] = "Sub Category successfully created!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_subcategory(self, subcategory_name):
        """Insert Category"""

        data = {}
        data['subcategory_name'] = subcategory_name
        data['created_on'] = time.time()

        subcategory_id = self.postgresql_query.insert('subcategory', data, 'subcategory_id')

        return subcategory_id or 0

    def insert_subcategory_options(self, subcategory_id, options):
        """Insert SubCategory Options"""

        data = {}
        data['subcategory_id'] = subcategory_id
        for opt in options:

            data['option'] = opt

            subcategory = self.postgresql_query.insert('subcategory_options', data,
                                                       str(subcategory_id))

            if not subcategory:
                return 0

        return subcategory

    def delete_subcategory(self, subcategory_id):
        """Delete Sub Category"""

        conditions = []

        conditions.append({
            "col": "subcategory_id",
            "con": "=",
            "val": subcategory_id
            })

        if self.postgresql_query.delete('subcategory', conditions):
            return 1

        return 0
