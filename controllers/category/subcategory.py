# pylint: disable=too-many-locals, invalid-name
"""SubCategory"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.couch_database import CouchDatabase
from library.couch_queries import Queries

class SubCategory(Common):
    """Class for SubCategory"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for SubCategory class"""
        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(SubCategory, self).__init__()

    def subcategory(self):
        """
        This API is for Getting Sub Category
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
            description: Sub Category
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
            # return self.return_data(data)

        # Sub Category DATA
        datas = self.get_subcategories(page, limit)
        datas['options'] = self.get_options()
        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_subcategories(self, page, limit):
        """Return List of SubCategories"""

        offset = int((page - 1) * limit)

        # COUNT
        sql_str = "SELECT COUNT(*) FROM subcategory"

        count = self.postgresql_query.query_fetch_one(sql_str)
        total_rows = count['count']

        # DATA
        sql_str = "SELECT c.*, (SELECT array_to_json(array_agg(co.option)) "
        sql_str += "FROM subcategory_options co WHERE c.subcategory_id=co.subcategory_id) "
        sql_str += "as options FROM subcategory c GROUP BY subcategory_id "
        sql_str += "LIMIT {0} OFFSET {1} ".format(limit, offset)

        res = self.postgresql_query.query_fetch_all(sql_str)


        total_page = int(math.ceil(int(total_rows - 1) / limit)) + 1

        data = {}
        data['rows'] = res
        data['total_rows'] = total_rows
        data['total_page'] = total_page
        data['limit'] = limit
        data['page'] = page

        return data


    def get_options(self):
        """Get Options"""

        # DATA
        sql_str = "SELECT DISTINCT option FROM option"

        datas = self.postgres.query_fetch_all(sql_str)
        data = []
        if datas:
            data = [temp_data['option'] for temp_data in datas]

            # REMOVE LINKED OPTIONS
            opt_sql = "SELECT array_to_json(array_agg(option)) as options"
            opt_sql += " FROM subcategory_options"
            res = self.postgresql_query.query_fetch_one(opt_sql)

            if res['options'] is not None:

                data = [dta for dta in data if dta not in res['options']]

        return data
