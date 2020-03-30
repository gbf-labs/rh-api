# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, too-many-locals, too-many-arguments, too-many-statements, too-many-instance-attributes
"""Invite"""
import string
import time
import json
from configparser import ConfigParser
import requests
from flask import  request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.sha_security import ShaSecurity
from library.postgresql_queries import PostgreSQL
from library.emailer import Email
from library.config_parser import config_section_parser
from templates.invitation import Invitation

class Invite(Common, ShaSecurity):
    """Class for Invite"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Invite class"""

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(Invite, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    # GET VESSEL FUNCTION
    def invitation(self):
        """
        This API is for Sending invitation
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
            description: Invite
            required: true
            schema:
              id: Invite
              properties:
                first_name:
                    type: string
                last_name:
                    type: string
                middle_name:
                    type: string
                url:
                    type: string
                email:
                    type: string
                companies:
                    types: array
                    example: []
                roles:
                    types: array
                    example: []
                vessels:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Sending invitaion
        """
        # INIT DATA
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET REQUEST PARAMS
        email = query_json["email"]
        url = query_json["url"]
        vessels = query_json['vessels']

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # INIT IMPORTANT KEYS
        important_keys = {}
        important_keys['companies'] = []
        important_keys['roles'] = []
        important_keys['email'] = "string"
        important_keys['url'] = "string"

        # CHECK IMPORTANT KEYS IN REQUEST JSON
        if not self.check_request_json(query_json, important_keys):

            data["alert"] = "Invalid query, Missing parameter!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # CHECK INVITATION
        if self.check_invitaion(email):
            data["alert"] = "Already invited!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        password = self.generate_password()

        # INSERT INVITATION
        account_id = self.insert_invitation(password, query_json)

        if not account_id:

            data = {}
            data['message'] = "Invalid email!"
            data['status'] = "Failed"

            return self.return_data(data)

        if self.vpn_db_build.upper() == 'TRUE':

            # FOR USER VPN
            # JOB DATAS
            callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
            data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"

            sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
            sql_str += "AND role_id in (SELECT role_id FROM role "
            sql_str += "WHERE role_name='super admin')"

            super_admin = self.postgres.query_fetch_one(sql_str)

            vpn_type = 'VCLIENT'
            cvpn_type = 'CLIENT'

            if super_admin:

                vpn_type = 'VRH'
                cvpn_type = 'RHADMIN'

            # INSERT JOB
            job_id = self.insert_job(callback_url,
                                     data_url,
                                     self.vpn_token,
                                     account_id,
                                     self.user_vpn,
                                     cvpn_type)

            # INIT PARAMS FOR CREATE VPN
            vpn_params = {}
            vpn_params['callback_url'] = callback_url
            vpn_params['data_url'] = data_url
            vpn_params['job_id'] = job_id

            # CREATE VPN
            self.create_vpn(vpn_params, self.vpn_token)

            # FOR VESSEL VPN
            if vessels or super_admin:

                allow_access = False

                for vessel in vessels:

                    if vessel['allow_access']:

                        allow_access = True
                        break

                if allow_access or super_admin:

                    # INSERT JOB
                    job_id = self.insert_job(callback_url,
                                             data_url,
                                             self.vpn_token,
                                             account_id,
                                             self.vessel_vpn,
                                             vpn_type)

                    # INIT PARAMS FOR CREATE VPN
                    vpn_params = {}
                    vpn_params['callback_url'] = callback_url
                    vpn_params['data_url'] = data_url
                    vpn_params['job_id'] = job_id

                    # CREATE VPN
                    self.create_vpn(vpn_params, self.vpn_token, True)

        # SEND INVITATION
        self.send_invitation(email, password, url)

        data = {}
        data['message'] = "Invitation successfully sent!"
        data['status'] = "ok"

        return self.return_data(data)

    def check_invitaion(self, email):
        """Check Invitation"""

        sql_str = "SELECT * FROM account WHERE "
        sql_str += " email = '" + email + "'"

        res = self.postgres.query_fetch_one(sql_str)

        if res:

            return res

        return 0

    def check_username(self, username):
        """Check Invitation"""

        sql_str = "SELECT * FROM account WHERE "
        sql_str += " username = '" + username + "'"

        res = self.postgres.query_fetch_one(sql_str)

        if res:

            return res

        return 0

    def insert_invitation(self, password, query_json):
        """Insert Invitation"""

        token = self.generate_token()

        vessels = query_json['vessels']
        companies = query_json['companies']
        roles = query_json['roles']

        data = query_json
        data = self.remove_key(data, "companies")
        data = self.remove_key(data, "roles")
        data = self.remove_key(data, "vessels")

        # username = query_json["email"].split("@")[0]

        username = "no_username_{0}".format(int(time.time()))
        if not self.check_username(username):
            username += self.random_str_generator(5)

        data['username'] = username
        data['token'] = token
        data['status'] = True
        data['state'] = False
        data['password'] = self.string_to_sha_plus(password)
        data['created_on'] = time.time()
        account_id = self.postgres.insert('account', data, 'id')

        if not account_id:
            return 0

        for vessel in vessels:

            ntwconf = self.couch_query.get_complete_values(
                vessel['vessel_id'],
                "NTWCONF"
            )

            # ACCOUNT VESSEL
            temp = {}
            temp['vessel_vpn_ip'] = ntwconf['NTWCONF']['tun1']['IP']
            temp['account_id'] = account_id
            temp['vessel_id'] = vessel['vessel_id']
            temp['vessel_vpn_state'] = 'pending'

            temp['allow_access'] = False
            if 'allow_access' in vessel.keys():
                temp['allow_access'] = vessel['allow_access']

            self.postgres.insert('account_vessel', temp)

        for company in companies:

            # ACCOUNT COMPANY
            temp = {}
            temp['account_id'] = account_id
            temp['company_id'] = company
            self.postgres.insert('account_company', temp)

        for role_id in roles:

            # ACCOUNT COMPANY
            temp = {}
            temp['account_id'] = account_id
            temp['role_id'] = role_id
            self.postgres.insert('account_role', temp)

        return account_id

    def send_invitation(self, email, password, url):
        """Send Invitation"""

        email_temp = Invitation()
        emailer = Email()

        message = email_temp.invitation_temp(password, url)
        subject = "Invitation"
        emailer.send_email(email, message, subject)

        return 1

    def generate_password(self):
        """Generate Password"""

        char = string.ascii_uppercase
        char += string.ascii_lowercase
        char += string.digits

        return self.random_str_generator(8, char)

    def insert_job(self, callback_url, data_url, vpn_token, account_id, user_vpn, vpn_type):
        """Insert Job"""

        update_on = time.time()

        # INIT NEW JOB
        temp = {}
        temp['callback_url'] = callback_url
        temp['vnp_server_ip'] = user_vpn
        temp['data_url'] = data_url
        temp['token'] = vpn_token
        temp['status'] = 'pending'
        temp['account_id'] = account_id
        temp['vpn_type'] = vpn_type
        temp['action'] = 'CREATE'
        temp['account_os'] = 'WINDOWS' # LINUX
        temp['update_on'] = update_on
        temp['created_on'] = update_on

        # INSERT NEW JOB
        job_id = self.postgres.insert('job',
                                      temp,
                                      'job_id'
                                     )

        return job_id

    def create_vpn(self, data, vpn_token, flag=False):
        """Create VPN"""
        api_endpoint = self.user_protocol + "://" + self.user_vpn + "/ovpn"

        if flag:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/ovpn"

        headers = {'content-type': 'application/json', 'token': vpn_token}

        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res
