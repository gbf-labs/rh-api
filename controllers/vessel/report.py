"""Report"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.couch_database import CouchDatabase
from library.couch_queries import Queries

class Report(Common):
    """Class for Report"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Report class"""
        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(Report, self).__init__()

    def report(self):
        """
        This API is for Getting Report Temp
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
          - name: vessel_id
            in: query
            description: Vessel ID
            required: true
            type: string
        responses:
          500:
            description: Error
          200:
            description: Report Temp
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # OPEN CONNECTION
        self.postgresql_query.connection()

        # GET REPORT TEMP
        report_data = self.get_report(vessel_id)

        # CLOSE CONNECTION
        self.postgresql_query.close_connection()

        datas = {}
        datas['report_data'] = report_data
        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_report(self, vessel_id):
        """Returns the Report"""

        sql_str = "SELECT * FROM report_temp WHERE vessel_id = '" + vessel_id + "'"

        res = self.postgresql_query.query_fetch_one(sql_str)

        if res:

            return res['report_data']

        default_report_data = "General Info: \n"
        default_report_data += """VESSEL: *["PARAMETERS"]["INFO"]["VESSELNAME"]*\n"""
        default_report_data += "TIME: *TIMESTAMP*\n"

        return default_report_data
