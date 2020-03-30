# pylint: disable=too-many-arguments, too-many-instance-attributes
"""Enable User"""
import time
import json

from configparser import ConfigParser
import requests
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class EnableUser(Common):
    """Class for EnableUser"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for EnableUser class"""

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.postgres = PostgreSQL()

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(EnableUser, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

    def enable_user(self):
        """
        This API is for Deleting User
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
            description: User IDs
            required: true
            schema:
              id: Delete Users
              properties:
                user_ids:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Delete User
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        user_ids = query_json["user_ids"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.enable_users(user_ids):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Users successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def enable_users(self, user_ids):
        """Enable Users"""

        conditions = []

        conditions.append({
            "col": "id",
            "con": "in",
            "val": user_ids
            })
        query_json = {}
        query_json['status'] = True

        for user_id in user_ids:

            if self.vpn_db_build.upper() == 'TRUE':

                # JOB DATAS
                callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
                data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"
                vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

                sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(user_id)
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
                                         vpn_token,
                                         user_id,
                                         self.user_vpn,
                                         'CREATE',
                                         cvpn_type)

                # INIT PARAMS FOR CREATE VPN
                vpn_params = {}
                vpn_params['callback_url'] = callback_url
                vpn_params['data_url'] = data_url
                vpn_params['job_id'] = job_id

                # CREATE VPN
                self.new_vpn(vpn_params, vpn_token, False)

                # VESSEL
                if self.get_user_vessels(user_id) or super_admin:

                    # INSERT JOB
                    job_id = self.insert_job(callback_url,
                                             data_url,
                                             vpn_token,
                                             user_id,
                                             self.vessel_vpn,
                                             'CREATE',
                                             vpn_type)

                    # INIT PARAMS FOR CREATE VPN
                    vpn_params = {}
                    vpn_params['callback_url'] = callback_url
                    vpn_params['data_url'] = data_url
                    vpn_params['job_id'] = job_id

                    # CREATE VPN
                    self.update_vpn(vpn_params, vpn_token, True)

        if self.postgres.update('account', query_json, conditions):

            return 1

        return 0

    def insert_job(self, callback_url, data_url, vpn_token, account_id, user_vpn, action, vpn_type):
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
        temp['action'] = action
        temp['account_os'] = 'WINDOWS' # LINUX
        temp['update_on'] = update_on
        temp['created_on'] = update_on

        # INSERT NEW JOB
        job_id = self.postgres.insert('job',
                                      temp,
                                      'job_id'
                                     )

        return job_id

    def new_vpn(self, data, vpn_token, flag=False):
        """New VPN"""

        api_endpoint = self.user_protocol + "://" + self.user_vpn + "/ovpn"

        if flag:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/ovpn"

        headers = {'content-type': 'application/json', 'token': vpn_token}

        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res

    def get_user_vessels(self, account_id):
        """Return User Vessels"""

        sql_str = "SELECT * FROM account_vessel WHERE account_id={0}".format(account_id)
        avs = self.postgres.query_fetch_all(sql_str)

        if avs:

            for acct in avs:

                if acct['allow_access']:

                    return 1

        return 0

    def update_vpn(self, data, vpn_token, flag=False):
        """Update VPN"""

        api_endpoint = self.user_protocol + "://" + self.user_vpn + "/ovpn"

        if flag:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/ovpn"

        headers = {'content-type': 'application/json', 'token': vpn_token}

        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res
