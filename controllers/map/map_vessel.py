#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=no-self-use, too-many-locals, too-many-statements, too-many-instance-attributes
"""Vessels"""
import time

from configparser import ConfigParser
from flask import request
from library.couch_database import CouchDatabase
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.common import Common
from library.aws_s3 import AwsS3
from library.config_parser import config_section_parser

class MapVessels(Common):
    """Class for Vessels"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Vessels class"""
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763
        self.vessel_name = ""
        self.aws3 = AwsS3()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']

        super(MapVessels, self).__init__()

    # GET VESSEL FUNCTION
    def map_vessels(self):
        """
        This API is for Getting Vessels
        ---
        tags:
          - Map
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
          - name: vessel_number
            in: query
            description: Vessel Number
            required: false
            type: string
        responses:
          500:
            description: Error
          200:
            description: Vessel Information
        """
        # INIT DATA
        data = {}

        # VESSEL ID
        vessel_number = request.args.get('vessel_number')
        vessels = []
        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        sql_str = "SELECT * FROM vessel "
        if not vessel_number:
            # COUCH QUERY - GET VESSELS

            sql_str += " ORDER BY created_on DESC"
            vessels = self.postgres.query_fetch_all(sql_str)

        else:
            # COUCH QUERY - GET VESSEL
            sql_str += "WHERE number='{0}'".format(vessel_number)

            vessels = self.postgres.query_fetch_all(sql_str)

        # CHECK DATABASES
        rows = []
        if vessels:

            vessel_ids = [x['vessel_id'] for x in vessels]

            # INIT SQL QUERY
            if len(vessel_ids) == 1:
                sql_str = "SELECT * FROM vessel WHERE state ='1'"
                sql_str += " AND vessel_id IN ('{0}')".format(vessel_ids[0])
            else:
                sql_str = "SELECT * FROM vessel WHERE state ='1'"
                sql_str += " AND vessel_id IN {0}".format(tuple(vessel_ids))

            # FETCH ALL
            vessels_state = self.postgres.query_fetch_all(sql_str)

            to_be_install = [x['vessel_id'] for x in vessels_state]
            # INIT VARIABLES

            # LOOP DATABASES
            for item in vessels:

                if not item['number'] == item['vessel_id']:

                    row = {}

                    # CONNECT TO DATABASE
                    # GET VESSEL NAME

                    # VESSEL POSIBLE STATE
                    # To be installed = 1
                    # Installed and etc. = 2

                    vessel_name = self.get_vessel_name(item['vessel_id'], item['number'])
                    self.vessel_name = vessel_name


                    mail_enable = self.get_email_schedule(item['vessel_id'])
                    last_update = self.get_last_update_with_option(item['vessel_id'])

                    epoch_time = int(time.time())

                    update_state = 'red'
                    if not item['vessel_id'] == item['number']:

                        update_state = self.check_time_lapse(epoch_time, last_update)

                    vpn_url = self.get_vpn_url(item['number'])

                    # SET THE RETURN VALUE
                    row['vessel_id'] = item['vessel_id']
                    row['vessel_rev'] = self.get_rev_id(item['vessel_id'], item['number'])
                    row['vessel_number'] = item['number']
                    row['vessel_name'] = vessel_name
                    row['mail_enable'] = mail_enable['mail_enable']
                    row['schedules'] = mail_enable['schedules']
                    row['emails'] = mail_enable['emails']
                    row['update_state'] = update_state
                    row['vpn_url'] = vpn_url

                    # GET IMAGE URL
                    row['image_url'] = self.aws3.get_vessel_image(item['vessel_id'])

                    if item['vessel_id'] in to_be_install:
                        row['update_state'] = 'white'

                    rows.append(row)

        # SET RETURN
        data['rows'] = rows
        data['status'] = 'ok'

        # RETURN
        return self.return_data(data)

    # GET THE VESSEL NAME
    def get_vessel_name(self, vessel_id, number):
        """Return Vessel Name"""

        if vessel_id == number:
            vessel_name = ""
            if self.vpn_db_build.upper() == 'TRUE':

                sql_str = "SELECT vessel_name FROM vessel_vpn_job WHERE imo='{0}' ".format(number)
                sql_str += "AND vpn_type='VESSEL' ORDER BY created_on DESC LIMIT 1"
                vname = self.postgres.query_fetch_one(sql_str)
                vessel_name = vname['vessel_name']

            else:

                sql_str = "SELECT vessel_name FROM vessel WHERE number='{0}'".format(number)
                vname = self.postgres.query_fetch_one(sql_str)
                vessel_name = vname['vessel_name']

            return vessel_name

        values = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )
        if values:
            return values['PARAMETERS']['INFO']['VESSELNAME']
        return ''

    def get_email_schedule(self, vessel_id):
        """Return Email Schedule"""

        # SQL QUERY
        cols = 'email_vessel_id, mail_enable, email'
        sql_str = "SELECT " + cols + " FROM email_vessel"
        sql_str += " WHERE vessel_id='{}'".format(vessel_id)

        # FETCH ONE
        email_vessels = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['emails'] = []
        data['schedules'] = []
        data['mail_enable'] = False

        if email_vessels:
            mail_enable = email_vessels[0]['mail_enable']
            email_vessel_id = email_vessels[0]['email_vessel_id']

            # SQL QUERY
            cols = 'schedule'
            sql_str = "SELECT " + cols + " FROM email_schedule"
            sql_str += " WHERE email_vessel_id='{}'".format(email_vessel_id)
            schedules = self.postgres.query_fetch_all(sql_str)

            data['emails'] = (list(map(lambda x: x['email'], email_vessels)))
            data['schedules'] = (list(map(lambda x: x['schedule'], schedules)))
            data['mail_enable'] = mail_enable

        return data

    def get_last_update_with_option(self, vessel_id):
        """Return Last Update with Option"""
        values = self.couch_query.get_complete_values(
            vessel_id,
            "COREVALUES",
            flag='one_doc'
        )

        if values:
            return values['timestamp']
        return ''

    def get_vpn_url(self, vessel_number):
        """ GET VPN URL """

        vpn_url = ""

        sql_str = "SELECT * FROM vessel_vpn_job WHERE"
        sql_str += " imo='{0}' AND status='active'".format(vessel_number)
        job = self.postgres.query_fetch_one(sql_str)

        if job:

            filename = job['directory'].split("/")[-1]
            created_on = job['created_on']
            # vpn_url = "download/vpn/{0}".format(filename)
            vpn_url = "download/vessel/vpn/{0}_{1}".format(created_on, filename)

        return vpn_url

    def get_rev_id(self, vessel_id, vessel_number):
        """ GET REV ID """

        if vessel_id == vessel_number:

            return vessel_id

        vessel = self.couch_query.get_vessels(vessel_number=vessel_number)
        if vessel:

            return vessel[0]['doc']['_rev']

        return 0
