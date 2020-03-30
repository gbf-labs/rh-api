# encoding: utf-8
# pylint: disable=no-self-use, bare-except
"""Noon Report CSV"""
# import math
import csv
import time
from datetime import datetime
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.unit_conversion import UnitConversion
# from library.couch_database import CouchDatabase
# from library.couch_queries import Queries
# from flask import send_file

class NoonReportCSV(Common):
    """Class for NoonReportCSV"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for NoonReportCSV class"""
        self.postgresql_query = PostgreSQL()
        self.unit_conversion = UnitConversion()
        super(NoonReportCSV, self).__init__()

    def noon_report_csv(self):
        """
        This API is to get noon report
        ---
        tags:
          - Email
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
          - name: mail_log_ids
            in: query
            description: Mail log ID's
            required: true
            type: string

        responses:
          500:
            description: Error
          200:
            description: Permission
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        mail_log_ids = request.args.get('mail_log_ids')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        outfile = "csv/" + str(int(time.time())) + "_noon_report.csv"

        self.generate_csv(mail_log_ids, outfile)

        datas = {}
        datas['location'] = outfile
        datas['status'] = 'ok'

        return self.return_data(datas)

    def generate_csv(self, mail_log_ids, outfile):
        """Generate CSV"""

        # MAIL LOG IDs
        if len(mail_log_ids.split(",")) == 1:
            mlis = "(" + str(mail_log_ids) +")"
        else:

            mlis = tuple(mail_log_ids.split(","))

        sql_str = "SELECT el.mail_log_id,el.message,el.data_date,el.created_on,ev.email FROM"
        sql_str += " email_log el INNER JOIN email_vessel ev ON"
        sql_str += " el.email_vessel_id=ev.email_vessel_id WHERE"
        sql_str += " mail_log_id in " + str(mlis)
        rows = self.postgresql_query.query_fetch_all(sql_str)

        headers = ["DATE SENT"]
        headers = headers + self.get_headers(rows)

        self.set_values(headers, rows, outfile)

        return 0

    def set_values(self, headers, rows, outfile):
        """ Set Values """

        with open(outfile, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            for row in rows:
                data = {}

                for mssg in row['message']:

                    defaults = ["General Info", "VSAT Info", "Failover Info"]
                    if mssg['label'] and mssg['label'] not in defaults:
                        data[mssg['label']] = mssg['value']

                utc = datetime.utcfromtimestamp(row['created_on']).strftime('%d %B %Y %I:%M:%S %p')
                date_send = utc + " UTC"

                data['DATE SENT'] = str(date_send)
                data['RECIPIENT'] = row['email']
                if row['data_date']:

                    data['AS of'] = row['data_date'].split(",")[1]

                writer.writerow(data)

    def get_headers(self, rows):
        """ Get Headers """

        headers = set()
        headers.add("AS of")
        headers.add("RECIPIENT")
        for row in rows:
            headers.update({x['label'] for x in row['message']})

        headers.discard("General Info")
        headers.discard("VSAT Info")
        headers.discard("Failover Info")

        return list(filter(None, headers))
