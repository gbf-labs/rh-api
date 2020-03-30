# pylint: disable=bare-except
"""Report Update"""
import time
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.couch_database import CouchDatabase
from library.couch_queries import Queries

class ReportUpdate(Common):
    """Class for ReportUpdate"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for ReportUpdate class"""
        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(ReportUpdate, self).__init__()

    def report_update(self):
        """
        This API is for Updating Report
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
            description: Report Temp
            required: true
            schema:
              id: ReportTemp
              properties:
                report_data:
                    type: string
                vessel_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Updating Report
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        query_json = request.get_json(force=True)

        # EXTRACT QUERY JSON
        report_data = query_json['report_data']
        vessel_ids = query_json['vessel_ids']

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # OPEN CONNECTION
        # self.postgresql_query.connection()

        for vessel_id in vessel_ids:

            # UPDATE VESSEL REPORT
            self.update_vessel_report(vessel_id, report_data)

        # CLOSE CONNECTION
        # self.postgresql_query.close_connection()

        datas = {}
        datas['status'] = 'ok'

        return self.return_data(datas)

    def update_vessel_report(self, vessel_id, report_data):
        """Update Vessel Report"""

        try:
            conditions = []

            conditions.append({
                "col": "vessel_id",
                "con": "=",
                "val": vessel_id
                })

            self.postgres.delete('report_temp', conditions)

        except:
            # print("New Report Temp")
            pass

        finally:

            data = {}
            data['vessel_id'] = vessel_id
            data['report_data'] = report_data
            data['state'] = True
            data['update_on'] = time.time()
            data['created_on'] = time.time()

            self.postgresql_query.insert('report_temp', data, 'report_temp_id')

        return 1
