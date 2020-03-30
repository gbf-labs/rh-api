"""Delete Vessel File"""
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

    def delete_file(self):
        """
        This API is for Deleting Files
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
            description: Vessel File(s)
            required: true
            schema:
              id: Delete Vessel Files
              properties:
                vessel_id :
                    type: string
                vessel_files:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete Vessel Files
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        vessel_files = query_json["vessel_files"]
        vessel_id = query_json["vessel_id"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.delete_vessel_file(vessel_id, vessel_files):

            data["alert"] = "Please check your query! | Failed to Delete File"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "File(s) successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def delete_vessel_file(self, vessel_id, filenames):
        """Delete Vessel File"""

        assert vessel_id, "Vessel ID is required."
        assert filenames, "File Name is required."

        files = ','.join(["'{}'".format(filename) for filename in filenames])
        print(files)
        # VERIFY IF IMAGE EXISTS FOR VESSEL
        sql_str = "SELECT * FROM vessel_file"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND file_name IN ({0})".format(files)
        sql_str += " AND status = 'active'"

        vessel_file = self.postgres.query_fetch_all(sql_str)
        file_ids = [fid['vessel_file_id'] for fid in vessel_file]

        if vessel_file:

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "vessel_file_id",
                "con": "IN",
                "val": file_ids
                })

            update_column = {}
            update_column['update_on'] = time.time()
            update_column['status'] = "inactive"

            if self.postgres.update('vessel_file', update_column, conditions):
                return 1
            return 0

        return 0
