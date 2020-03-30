"""Delete SubCategory"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class DeleteSubCategory(Common):
    """Class for DeleteSubCategory"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteSubCategory class"""
        self.postgresql_query = PostgreSQL()
        super(DeleteSubCategory, self).__init__()

    def delete_subcategory(self):
        """
        This API is for Deleting Sub Category
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
            description: SubCategory IDs
            required: true
            schema:
              id: Delete SubCategories
              properties:
                subcategory_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Sub Category
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        subcategory_ids = query_json["subcategory_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_subcategories(subcategory_ids):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Sub Category successfully deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_subcategories(self, subcategory_ids):
        """Delete Sub Categories"""

        conditions = []

        conditions.append({
            "col": "subcategory_id",
            "con": "in",
            "val": subcategory_ids
            })

        if self.postgresql_query.delete('subcategory', conditions):

            return 1

        return 0
