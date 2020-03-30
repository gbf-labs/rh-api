# encoding: utf-8
# pylint: disable=no-self-use, too-many-arguments, bare-except
"""Noon Report Data"""
# import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.unit_conversion import UnitConversion
# from library.couch_database import CouchDatabase
# from library.couch_queries import Queries

class NoonReportData(Common):
    """Class for NoonReportData"""
    # INITIALIZE
    def __init__(self):
        """The Constructor for NoonReportData class """
        self.postgresql_query = PostgreSQL()
        self.unit_conversion = UnitConversion()
        super(NoonReportData, self).__init__()

    def noon_report_data(self):
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

        # COMPANY DATA
        datas = self.get_noon_report_data(mail_log_ids)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_noon_report_data(self, mail_log_ids):
        """Return Noon Report Data"""

        # MAIL LOG IDs
        if len(mail_log_ids.split(",")) == 1:
            mlis = "(" + str(mail_log_ids) +")"
        else:

            mlis = tuple(mail_log_ids.split(","))

        sql_str = "SELECT mail_log_id,message,data_date FROM email_log  WHERE "
        sql_str += "mail_log_id in " + str(mlis)

        datas = self.postgresql_query.query_fetch_all(sql_str)

        rows = []
        for data in datas or []:
            temp = {}
            msg = ""
            msg += "As of " + data['data_date'] + "\n\n"

            for message in data['message']:
                if message['label'] == "":
                    msg += "\n"
                else:

                    try:

                        # if message['label'] == "LATITUDE":
                        #     latitude = self.to_degrees(message['value'])

                        #     lat_cardinal = "S"
                        #     if float(message['value']) >= 0: lat_cardinal = "N"

                        #     message['value'] = str(latitude) + " " + str(lat_cardinal)

                        # elif message['label'] == "LONGITUDE":

                        #     longitude = self.to_degrees(message['value'])

                        #     long_cardinal = "W"
                        #     if float(message['value']) >= 0: long_cardinal = "E"

                        #     message['value'] = str(longitude) + " " + str(long_cardinal)

                        if message['label'] in ["LATITUDE", "LONGITUDE"]:

                            message['value'] = self.unit_conversion.to_degrees(message['label'],
                                                                               message['value'])

                        elif message['label'] == "HEADING":

                            message['value'] = str(int(float(message['value']))) + "°"

                    except:

                        message['value'] = ""

                    msg += message['label'] + ": " + message['value'] + "\n"

            temp['message'] = msg
            temp['mail_log_id'] = data['mail_log_id']

            rows.append(temp)

        data = {}
        data['rows'] = rows

        return data

    # def to_degrees(self, coordinate):
    #     """Return data to degrees"""

    #     absolute = abs(float(coordinate))
    #     degrees = math.floor(absolute)
    #     minutes_not_truncated = (absolute - degrees) * 60
    #     minutes = math.floor(minutes_not_truncated)
    #     seconds = math.floor((minutes_not_truncated - minutes) * 60)

    #     return str(degrees) + "° " + str(minutes) + "' " + str(seconds) + "''"
