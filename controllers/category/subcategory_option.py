"""SubCategory Option"""
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_database import CouchDatabase
from library.couch_queries import Queries


class SubCategoryOption(Common):
    """Class for CreateSubCategoryOption"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for SubCategoryOption class"""

        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(SubCategoryOption, self).__init__()

    def subcategory_option(self):
        """
        This API is for Linking Sub Category Options
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
              id: SubCategory Options
              properties:
                subcategory_id:
                    type: string
                options:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Sub Category Options
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

        # CREATE SUBCATEGORY

        if not self.insert_subcategory_options(query_json):
            data["alert"] = "Please check your query! | Sub Category or Options already exist."
            data['status'] = 'Failed'
            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Options linked successfully!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_subcategory_options(self, query_json):
        """Insert SubCategory Options"""

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
                                                       query_json['subcategory_id'])

            if not subcategory:
                return 0

        return subcategory
