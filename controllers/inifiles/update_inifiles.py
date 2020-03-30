# pylint: disable=too-many-instance-attributes
"""Update Role"""
import time
import json
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdateINIFiles(Common):
    """Class for Update INI Files"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Update INI Files class"""
        self.postgres = PostgreSQL()
        super(UpdateINIFiles, self).__init__()

    def update_inifiles(self):
        """
        This API is for Update INI Files
        ---
        tags:
          - INI Files
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
            description: Update INI Files
            required: true
            schema:
              id: Update INI Files
              properties:
                datas:
                    type: json
                    example: {}
                vessel_id:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Update INI Files
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)
        vessel_id = query_json['vessel_id']
        inidatas = query_json['datas']

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

        if not self.update_ini_datas(vessel_id, inidatas):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "INI Files successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_ini_datas(self, vessel_id, inidatas):
        """Update INI Files"""

        update_time = time.time()

        updates = True

        for vdata in inidatas.keys():

            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "vessel_id",
                "con": "=",
                "val": vessel_id
                })

            conditions.append({
                "col": "dir",
                "con": "=",
                "val": vdata
                })

            new_data = {}
            new_data['content'] = json.dumps(inidatas[vdata].split("\n"))
            new_data['lastupdate'] = update_time
            new_data['vessel_lastupdate'] = update_time

            # UPDATE INI FILES
            if not self.postgres.update('ini_files', new_data, conditions):

                updates = False

        if not updates:
            # RETURN
            return 0

        # RETURN
        return 1
