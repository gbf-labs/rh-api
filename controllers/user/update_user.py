# pylint: disable=too-many-locals, too-many-arguments, too-many-statements, too-many-branches, too-many-instance-attributes
"""Update User"""
import time
import json

from configparser import ConfigParser
import requests
from flask import  request
from library.common import Common
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class UpdateUser(Common):
    """Class for UpdateUser"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateUser class"""

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(UpdateUser, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    def update_user(self):
        """
        This API is for Updating User
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
            description: Updating User
            required: true
            schema:
              id: Updating User
              properties:
                account_id:
                    type: string
                username:
                    type: string
                password:
                    type: string
                status:
                    type: boolean
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
            description: Updating User
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

        if not self.update_users(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "User successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_users(self, query_json):
        """Update Users"""

        # GET CURRENT TIME
        query_json['update_on'] = time.time()

        account_id = query_json['account_id']

        # GET SUPER ADMIN ACCOUNT
        sa_role = self.get_sa_role(account_id)

        superadmin = self.get_super_admin()

        roles = []
        companies = []
        vessels = []

        if 'roles' in query_json.keys():
            roles = query_json['roles']

        if 'companies' in query_json.keys():
            companies = query_json['companies']

        if 'vessels' in query_json.keys():
            vessels = query_json['vessels']

        status = self.get_user_status(account_id)

        if status and self.vpn_db_build.upper() == 'TRUE':

            # Client -> Super admin
            if superadmin['role_id'] in roles and not sa_role:
                self.delete_vpn_allow(account_id)
                self.create_vpn(account_id, 'super admin')

            # Super admin -> Client
            elif not superadmin['role_id'] in roles and sa_role:
                self.delete_vpn_allow(account_id, 'super admin')
                self.create_vpn(account_id)

        # UPDATE
        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "id",
            "con": "=",
            "val": account_id
            })

        # REMOVE KEYS
        query_json = self.remove_key(query_json, "account_id")
        query_json = self.remove_key(query_json, "roles")
        query_json = self.remove_key(query_json, "companies")
        query_json = self.remove_key(query_json, "vessels")

        # UPDATE ROLE
        if self.postgres.update('account', query_json, conditions):

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "account_id",
                "con": "=",
                "val": account_id
                })

            # ROLES
            if roles:

                # DELETE OLD PERMISSION
                self.postgres.delete('account_role', conditions)

                # LOOP NEW PERMISSIONS
                for role_id in roles:

                    # INIT NEW PERMISSION
                    temp = {}
                    temp['account_id'] = account_id
                    temp['role_id'] = role_id

                    # INSERT NEW PERMISSION OF ROLE
                    self.postgres.insert('account_role', temp)

            # COMPANIES
            if companies:

                # DELETE OLD COMPANY
                self.postgres.delete('account_company', conditions)

                # LOOP NEW COMPANIES
                for company_id in companies:

                    # INIT NEW COMPANY
                    temp = {}
                    temp['account_id'] = account_id
                    temp['company_id'] = company_id

                    # INSERT NEW COMPANY
                    self.postgres.insert('account_company', temp)

            # VESSELS
            if vessels:

                # DELETE OLD VESSELS
                self.postgres.delete('account_vessel', conditions)

                # REMOVE VNP ACCESS ON VESSEL FLAG
                vpn_acces = True

                # LOOP NEW VESSELS
                for vessel in vessels:

                    ntwconf = self.couch_query.get_complete_values(
                        vessel['vessel_id'],
                        "NTWCONF"
                    )
                    # INIT NEW VESSEL
                    temp = {}
                    temp['vessel_vpn_ip'] = ntwconf['NTWCONF']['tun1']['IP']
                    temp['account_id'] = account_id
                    temp['vessel_id'] = vessel['vessel_id']
                    temp['allow_access'] = vessel['allow_access']
                    temp['vessel_vpn_state'] = 'pending'

                    # INSERT NEW ACCOUNT VESSEL
                    self.postgres.insert('account_vessel', temp)

                    if not vessel['allow_access']:
                        vpn_acces = False

                if status and self.vpn_db_build.upper() == 'TRUE':

                    if not vpn_acces or sa_role:

                        callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
                        data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"

                        vpn_type = 'VCLIENT'

                        # INSERT JOB
                        job_id = self.insert_job(callback_url,
                                                 data_url,
                                                 self.vpn_token,
                                                 account_id,
                                                 self.vessel_vpn,
                                                 'REMOVE',
                                                 vpn_type)

                        # INIT PARAMS FOR REMOVE VPN
                        vpn_params = {}
                        vpn_params['callback_url'] = callback_url
                        vpn_params['data_url'] = data_url
                        vpn_params['job_id'] = job_id

                        self.remove_vpn_ip(vpn_params, self.vpn_token, True)

            # RETURN
            return 1

        # RETURN
        return 0

    def remove_vpn_ip(self, data, vpn_token, flag=False):
        """Remove VPN IP"""

        api_endpoint = self.user_protocol + "://" + self.user_vpn + "/ovpn"

        if flag:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/ovpn"

        headers = {'content-type': 'application/json', 'token': vpn_token}

        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res

    def insert_job(self, callback_url, data_url, vpn_token,
                   account_id, user_vpn, action, vpn_type):
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

    def get_sa_role(self, account_id):
        """Return Super Admin Role"""

        sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
        sql_str += "AND role_id in (SELECT role_id FROM role "
        sql_str += "WHERE role_name='super admin')"

        account = self.postgres.query_fetch_one(sql_str)

        return account

    def get_super_admin(self):
        """Return Super Admin"""

        sql_str = "SELECT * FROM role WHERE role_name='super admin'"

        super_admin = self.postgres.query_fetch_one(sql_str)

        return super_admin


    def delete_vpn_allow(self, account_id, super_admin=False):
        """Delete VPN Allow"""

        if self.vpn_db_build.upper() == 'TRUE':

            callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
            data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"
            vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

            vpn_type = 'VCLIENT'
            cvpn_type = 'CLIENT'

            # SUPER ADMIN TO CLIENT
            if super_admin:

                vpn_type = 'VRH'
                cvpn_type = 'RHADMIN'

            # CLIENT
            # INSERT JOB
            job_id = self.insert_job(callback_url,
                                     data_url,
                                     vpn_token,
                                     account_id,
                                     self.user_vpn,
                                     'DELETE',
                                     cvpn_type)

            # INIT PARAMS FOR UPDATE VPN
            vpn_params = {}
            vpn_params['callback_url'] = callback_url
            vpn_params['data_url'] = data_url
            vpn_params['job_id'] = job_id

            # UPDATE VPN
            self.update_vpn(vpn_params, vpn_token)

        # VESSEL
        if self.get_user_vessels(account_id) or super_admin:

            # print("DELETE VCLIENT/VHR VPN")
            # INSERT JOB
            job_id = self.insert_job(callback_url,
                                     data_url,
                                     vpn_token,
                                     account_id,
                                     self.vessel_vpn,
                                     'DELETE',
                                     vpn_type)

            # INIT PARAMS FOR UPDATE VPN
            vpn_params = {}
            vpn_params['callback_url'] = callback_url
            vpn_params['data_url'] = data_url
            vpn_params['job_id'] = job_id

            # UPDATE VPN
            self.update_vpn(vpn_params, vpn_token, True)

        conditions = []

        conditions.append({
            "col": "id",
            "con": "=",
            "val": account_id
            })

        query_json = {}
        query_json['status'] = False

        if self.postgres.update('account', query_json, conditions):

            return 1

        return 0

    def create_vpn(self, account_id, super_admin=False):
        """Create VPN"""

        query_json = {}
        query_json['status'] = True

        if self.vpn_db_build.upper() == 'TRUE':

            # JOB DATAS
            callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
            data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"
            vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

            vpn_type = 'VCLIENT'
            cvpn_type = 'CLIENT'

            if super_admin:

                vpn_type = 'VRH'
                cvpn_type = 'RHADMIN'

            # INSERT JOB
            job_id = self.insert_job(callback_url,
                                     data_url,
                                     vpn_token,
                                     account_id,
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
            if self.get_user_vessels(account_id) or super_admin:

                # INSERT JOB
                job_id = self.insert_job(callback_url,
                                         data_url,
                                         vpn_token,
                                         account_id,
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

        conditions = []

        conditions.append({
            "col": "id",
            "con": "=",
            "val": account_id
            })

        if self.postgres.update('account', query_json, conditions):

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

    def get_user_status(self, account_id):
        """Return User Status"""

        sql_str = "SELECT status FROM account WHERE id={0}".format(account_id)
        account = self.postgres.query_fetch_one(sql_str)

        return account['status']
