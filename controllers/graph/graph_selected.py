"""Graph Selected"""
import time

from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class GraphSelected(Common):
    """Class for GraphSelected"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for GraphSelected class"""
        self.postgres = PostgreSQL()
        super(GraphSelected, self).__init__()

    def graph_selected(self):
        """
        This API is for Updating Graph Selected
        ---
        tags:
          - Graph
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
            description: Updating Graph Selected
            required: true
            schema:
              id: Updating Graph Selected
              properties:
                device_type:
                    type: string
                select_type:
                    type: string
                labels:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Updating Role
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

        if not self.update_graph_selected(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Selected graph successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_graph_selected(self, query_json):
        """Update Graph Selected"""

        # GET VALUES FOR LABELS
        labels = query_json['labels']
        device_type = query_json['device_type']
        select_type = query_json['select_type']

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "device_type",
            "con": "=",
            "val": device_type
            })

        conditions.append({
            "col": "select_type",
            "con": "=",
            "val": select_type
            })


        self.postgres.delete('selected_label', conditions)

        for label in labels:

            data = {}
            data['device_type'] = device_type
            data['select_type'] = select_type
            data['created_on'] = time.time()
            data['update_on'] = time.time()
            data['label'] = label

            self.postgres.insert('selected_label', data)

        return 1
