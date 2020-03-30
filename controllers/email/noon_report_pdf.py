# encoding: utf-8
# pylint: disable=no-self-use, bare-except
"""Noon Report PDF"""
# import math
import time
from datetime import datetime
from fpdf import FPDF
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.unit_conversion import UnitConversion
# from library.couch_database import CouchDatabase
# from library.couch_queries import Queries
# from flask import send_file

class NoonReportPDF(Common):
    """Class for NoonReportPDF"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for NoonReportPDF class"""
        self.postgresql_query = PostgreSQL()
        self.unit_conversion = UnitConversion()
        super(NoonReportPDF, self).__init__()

    def noon_report_pdf(self):
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

        output_file = "pdf/" + str(int(time.time())) + "_noon_report.pdf"

        pdf = self.generate_pdf(mail_log_ids)
        pdf.output(output_file, "F")

        datas = {}
        datas['location'] = output_file
        datas['status'] = 'ok'

        return self.return_data(datas)

    def generate_pdf(self, mail_log_ids):
        """Generate PDF"""

        # PDF SIZE Y, X
        pdf = FPDF('L', 'mm', (279.4, 215.9))

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

        header = "Noon report"

        for row in rows:
            pdf.add_page()

            self.render_header_data(pdf, header)

            self.render_details_data(pdf, row)
            self.render_footer_data(pdf)

        return pdf

    def render_details_data(self, pdf, details):
        """Render Details Data"""

        pdf.set_font('Arial', '', 10)
        start_y = 25

        data = "As of " + details['data_date']

        pdf.text(10, start_y, str(data))

        start_y += 10

        for info in details['message']:

            if info['label'] == "":

                start_y += 5

            else:

                try:

                    # if info['label'] == "LATITUDE":
                    #     latitude = self.to_degrees(info['value'])

                    #     lat_cardinal = "S"
                    #     if float(info['value']) >= 0: lat_cardinal = "N"

                    #     info['value'] = str(latitude) + " " + str(lat_cardinal)

                    # elif info['label'] == "LONGITUDE":

                    #     longitude = self.to_degrees(info['value'])

                    #     long_cardinal = "W"
                    #     if float(info['value']) >= 0: long_cardinal = "E"

                    #     info['value'] = str(longitude) + " " + str(long_cardinal)

                    if info['label'] in ["LATITUDE", "LONGITUDE"]:

                        info['value'] = self.unit_conversion.to_degrees(info['label'],
                                                                        info['value'])

                    elif info['label'] == "HEADING":

                        info['value'] = str(int(float(info['value']))) + "°"

                except:

                    info['value'] = ""


                data = info['label'] + ": " + info['value']

                pdf.text(10, start_y, str(data))

                start_y += 5

        start_y += 5
        # TIME AND DATE EMAIL SEND
        utc = datetime.utcfromtimestamp(details['created_on']).strftime('%A, %d %B %Y %I:%M:%S %p')
        date_send = utc + " UTC"

        data = "DATE SENT: " + str(date_send)
        pdf.text(10, start_y, str(data))
        start_y += 5

        # EMAIL RECIPIENT
        data = "RECIPIENT: " + details['email']
        pdf.text(10, start_y, str(data))
        start_y += 5

    def render_header_data(self, pdf, header):
        """Render Header Data"""

        # TITLE
        pdf.set_font('Courier', 'B', 16.5)
        top_width = pdf.get_string_width(header)
        pdf.text((top_width/2) + 65, 12, header)

    def render_footer_data(self, pdf):
        """Render Footer Data"""

        pdf.set_font('Arial', '', 8)

    # def to_degrees(self, coordinate):
    #     """Render To Degrees"""

    #     absolute = abs(float(coordinate))
    #     degrees = math.floor(absolute)
    #     minutes_not_truncated = (absolute - degrees) * 60
    #     minutes = math.floor(minutes_not_truncated)
    #     seconds = math.floor((minutes_not_truncated - minutes) * 60)

    #     return str(degrees) + "° " + str(minutes) + "' " + str(seconds) + "''"
