"""Delete Vessel Image"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class Delete(Common):
    """Class for Delete"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Delete class"""
        self.postgres = PostgreSQL()
        super(Delete, self).__init__()

    def delete_image(self):
        """
        This API is for Deleting Images
        ---
        tags:
          - Vessel
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
            description: Vessel IDs
            required: true
            schema:
              id: Delete Vessel IDs images
              properties:
                vessel_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Vessel Images
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        vessel_ids = query_json["vessel_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_vessel_images(vessel_ids):

            data["alert"] = "Please check your query! | Failed to Delete Image"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Images successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_vessel_images(self, vessel_ids):
        """Delete Vessel Images"""

        for vessel_id in vessel_ids:

            # VERIFY IF IMAGE EXISTS FOR VESSEL
            sql_str = "SELECT * FROM vessel_image"
            sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
            sql_str += " AND status = 'active'"

            vessel = self.postgres.query_fetch_one(sql_str)

            if vessel:

                # INIT CONDITION
                conditions = []

                # CONDITION FOR QUERY
                conditions.append({
                    "col": "vessel_image_id",
                    "con": "=",
                    "val": vessel['vessel_image_id']
                    })

                update_column = {}
                update_column['update_on'] = time.time()
                update_column['status'] = "inactive"

                if self.postgres.update('vessel_image', update_column, conditions):
                    return 1
                return 0

            return 0
