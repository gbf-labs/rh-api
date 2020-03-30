"""Update Vessel State"""
import time

from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdateVesselState(Common):
    """Class for UpdateVesselState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateVesselState class"""
        self.postgres = PostgreSQL()
        super(UpdateVesselState, self).__init__()

    def update_vessel_state(self):
        """
        This API is for Updating Vessel State
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
            description: Updating Vessel State
            required: true
            schema:
              id: Updating Vessel State
              properties:
                state:
                    type: string
                vessel_id:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Updating Vessel State
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

        if not self.vessel_state(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Update state successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def vessel_state(self, query_json):
        """Vessel State"""

        # GET CURRENT TIME

        updates = {}
        updates['state'] = query_json['state']
        updates['update_on'] = time.time()

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "vessel_id",
            "con": "=",
            "val": query_json['vessel_id']
            })

        self.postgres.update('vessel', updates, conditions)

        # RETURN
        return 1
