# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, too-many-locals
"""Reinvite"""
import string
from configparser import ConfigParser
from flask import  request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.sha_security import ShaSecurity
from library.postgresql_queries import PostgreSQL
from library.emailer import Email
from library.config_parser import config_section_parser
from templates.message import Message
from templates.invitation import Invitation

class Reinvite(Common, ShaSecurity):
    """Class for Reinvite"""
    # pylint: disable=too-many-instance-attributes
    # INITIALIZE
    def __init__(self):
        """The Constructor for Reinvite class"""
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(Reinvite, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    # GET VESSEL FUNCTION
    def reinvite(self):
        """
        This API is for Sending reinvite
        ---
        tags:
          - User
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
            description: Reinvite
            required: true
            schema:
              id: Reinvite
              properties:
                user_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Sending reinvitaion
        """
        # INIT DATA
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET REQUEST PARAMS
        user_ids = query_json["user_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        for user_id in user_ids:

            # CREATE SQL QUERY
            sql_str = "SELECT * FROM account WHERE id='" + str(user_id) + "'"

            res = self.postgres.query_fetch_one(sql_str)

            password = self.generate_password()

            items = {}
            items['password'] = self.string_to_sha_plus(password)

            # INSERT INVITATION
            self.update_invitation(user_id, items)

            # SEND INVITATION
            self.send_invitation(res['email'], password, res['url'])

            sql_str = "SELECT * FROM job WHERE job_id in ("
            sql_str += "SELECT job_id FROM account_vpn WHERE "
            sql_str += "account_id={0} and status=true)".format(user_id)

            jobs = self.postgres.query_fetch_all(sql_str)

            if self.vpn_db_build.upper() == 'TRUE':
                for job in jobs:

                    email = res['email']
                    filename = job['directory'].split("/")[-1]

                    vpn_dir = '/home/admin/all_vpn/' + filename

                    emailer = Email()
                    email_temp = Message()

                    message = email_temp.message_temp("Please see attached VPN.")
                    subject = "Web VPN"
                    if job['vpn_type'] in ['VCLIENT', 'VRH']:
                        subject = "Vessel VPN"

                    instruction = './Instructions_OPENVPN.pdf'
                    emailer.send_email(email,
                                       message,
                                       subject,
                                       [vpn_dir, instruction])

        data = {}
        data['message'] = "Re: Invitation successfully sent!"
        data['status'] = "ok"

        return self.return_data(data)

    def update_invitation(self, account_id, query_json):
        """Update Invitation"""

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "id",
            "con": "=",
            "val": account_id
            })

        self.postgres.update('account', query_json, conditions)

        return 1

    def send_invitation(self, email, password, url):
        """Send Invitation"""

        email_temp = Invitation()
        emailer = Email()

        message = email_temp.invitation_temp(password, url)
        subject = "Re-Invitation"
        emailer.send_email(email, message, subject, image="")

        return 1

    def generate_password(self):
        """Generate Password"""

        char = string.ascii_uppercase
        char += string.ascii_lowercase
        char += string.digits

        return self.random_str_generator(8, char)
