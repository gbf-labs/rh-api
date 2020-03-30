# pylint: disable=too-many-instance-attributes
"""VPN IP Update"""
import json
import time

from configparser import ConfigParser
import requests
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.couch_queries import Queries
from library.config_parser import config_section_parser

class VPNIPUpdate(Common):
    """Class for VPNIPUpdate"""
    # INITIALIZE
    def __init__(self):
        """The Constructor for VPNIPUpdate class"""

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(VPNIPUpdate, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']
            # self.generate_token()
            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'


    def vpn_ip_update(self):
        """VPN IP Update"""

        if self.vpn_db_build.upper() == 'TRUE':

            account_vpn_state = self.get_account_vpn_state()
            if account_vpn_state:
                self.update_account_vessel(account_vpn_state)

            account_vessels = self.get_account_vessel(True)

            for account_vessel in account_vessels or []:

                self.check_job(account_vessel, 'ADD')

            account_vessels = self.get_account_vessel(False)
            disabled_account = self.get_account_vessel(False, 'account_offline_vessel')
            account_vessels += disabled_account

            for account_vessel in account_vessels or []:

                self.check_job(account_vessel, 'REMOVE')

        return 1

    def get_account_vpn_state(self):
        """Return Account VPN State"""

        # INIT SQL QUERY
        sql_str = "SELECT * FROM account WHERE vessel_vpn_state='pending'"

        # FETCH ALL
        res = self.postgres.query_fetch_all(sql_str)

        # RETURN
        return res

    def get_account_vessel(self, allow_access, table="account_vessel"):
        """Return Account Vessel"""

        # INIT SQL QUERY
        sql_str = "SELECT DISTINCT (account_id), allow_access FROM {0}".format(table)
        sql_str += " WHERE vessel_vpn_state='pending' AND allow_access={0}".format(allow_access)

        # FETCH ALL
        res = self.postgres.query_fetch_all(sql_str)

        # RETURN
        return res

    def update_account_vessel(self, account_vpn_state):
        """Update Account Vessel"""

        for avs in account_vpn_state:
            account_id = avs['id']
            vessel_allow_access = self.get_vessel_allow_access(account_id)

            self.remove_account_vessel(account_id, vessel_allow_access)

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "id",
                "con": "=",
                "val": account_id
                })

            updates = {}
            updates['vessel_vpn_state'] = 'ok'

            # UPDATE VESSEL VPN STATE
            self.postgres.update('account', updates, conditions)

    def check_job(self, account, action):
        """Check Job"""

        account_id = account['account_id']
        # INIT SQL QUERY
        sql_str = "SELECT * FROM job"
        sql_str += " WHERE account_id='{0}' AND status='pending'".format(account_id)
        sql_str += " AND action='{0}'".format(action)
        res = self.postgres.query_fetch_one(sql_str)

        # JOB DATAS
        callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
        data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"

        if not res:
            user_vpn = self.get_user_vpn(account_id)

            if user_vpn:

                sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
                sql_str += "AND role_id in (SELECT role_id FROM role "
                sql_str += "WHERE role_name='super admin')"

                super_admin = self.postgres.query_fetch_one(sql_str)

                vpn_type = 'VCLIENT'

                if not super_admin:

                    # vpn_type = 'VRH'

                    update_on = time.time()

                    # INIT NEW JOB
                    temp = {}
                    temp['callback_url'] = callback_url
                    temp['vnp_server_ip'] = user_vpn
                    temp['data_url'] = data_url
                    temp['token'] = self.vpn_token
                    temp['status'] = 'pending'
                    temp['account_id'] = account_id
                    temp['vpn_type'] = vpn_type
                    temp['action'] = action
                    temp['update_on'] = update_on
                    temp['created_on'] = update_on

                    # INSERT NEW JOB
                    job_id = self.postgres.insert('job',
                                                  temp,
                                                  'job_id'
                                                 )

                    # INIT PARAMS FOR CREATE VPN
                    vpn_params = {}
                    vpn_params['callback_url'] = callback_url
                    vpn_params['data_url'] = data_url
                    vpn_params['job_id'] = job_id

                    self.add_vpn_ip(vpn_params, self.vpn_token, True)

                    return job_id

                return 0

        else:

            job_id = res['job_id']

            # INIT PARAMS FOR CREATE VPN
            vpn_params = {}
            vpn_params['callback_url'] = callback_url
            vpn_params['data_url'] = data_url
            vpn_params['job_id'] = job_id

            self.add_vpn_ip(vpn_params, self.vpn_token, True)

        return 0

    def get_user_vpn(self, account_id):
        """Return User VPN"""

        sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
        sql_str += "AND role_id in (SELECT role_id FROM role "
        sql_str += "WHERE role_name='super admin')"

        super_admin = self.postgres.query_fetch_one(sql_str)

        vpn_type = 'VCLIENT'

        if super_admin:

            vpn_type = 'VRH'

        # INIT SQL QUERY
        sql_str = "SELECT * FROM account_vpn"
        sql_str += " WHERE account_id='{0}' AND vpn_type='{1}'".format(account_id, vpn_type)
        sql_str += " ORDER BY created_on DESC LIMIT 1"
        res = self.postgres.query_fetch_one(sql_str)

        if res:

            return res['vpn_ip']

        return 0

    def add_vpn_ip(self, data, vpn_token, flag=False):
        """Add VPN IP"""

        api_endpoint = self.user_protocol + "://" + self.user_vpn + "/ovpn"

        if flag:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/ovpn"

        headers = {'content-type': 'application/json', 'token': vpn_token}
        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res

    def get_vessel_allow_access(self, account_id):
        """Return Vessel Allow Access"""

        # DATA
        sql_str = "SELECT * FROM account_company WHERE account_id = " + str(account_id)

        res = self.postgres.query_fetch_all(sql_str)

        rows = []

        # COMPANY'S VESSELS-ID
        for company in res:
            company_id = company['company_id']
            vessel_res = self.get_company_vessels(company_id)
            vessels = []
            for vessel in vessel_res['rows']:

                temp = {}
                temp['vessel_id'] = vessel['vessel_id']
                temp['allow_access'] = self.get_allow_access(account_id, vessel['vessel_id'])
                vessels.append(temp)

            company['vessels'] = vessels
            rows.append(company)

        temp_vessels = []
        list_vessels = []
        for row in rows:

            for row_vessel in row['vessels'] or []:

                if row_vessel['vessel_id'] not in list_vessels:

                    list_vessels.append(row_vessel['vessel_id'])
                    temp_vessels.append(row_vessel)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        return temp_vessels

    # GET VESSELS OF COMPANY
    def get_company_vessels(self, company_id):
        """Return Company Vessels"""

        assert company_id, "CompanyID is required."

        # DATA
        vessels = []
        sql_str = "SELECT * FROM company_vessels WHERE company_id={0}".format(company_id)
        vessels = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = vessels

        return data

    def get_allow_access(self, account_id, vessel_id):
        """Return Allow Access"""

        # DATA
        sql_str = "SELECT * FROM account_vessel"
        sql_str += " WHERE account_id={0} AND vessel_id='{1}'".format(account_id, vessel_id)
        vessel = self.postgres.query_fetch_one(sql_str)

        if vessel:

            return vessel['allow_access']

        ntwconf = self.couch_query.get_complete_values(
            vessel_id,
            "NTWCONF"
        )

        # INSERT ACCOUNT VESSEL
        temp = {}
        temp['vessel_vpn_ip'] = ntwconf['NTWCONF']['tun1']['IP']
        temp['account_id'] = account_id
        temp['vessel_id'] = vessel_id
        temp['allow_access'] = False
        temp['vessel_vpn_state'] = 'ok'
        self.postgres.insert('account_vessel', temp)

        return False

    def remove_account_vessel(self, account_id, vessel_allow_access):
        """Remove Account Vessel"""

        vessel_ids = [x['vessel_id'] for x in vessel_allow_access]

        if vessel_ids:

            # INIT SQL QUERY
            sql_str = "SELECT allow_access, vessel_id FROM account_vessel"

            if len(vessel_ids) == 1:

                sql_str += " WHERE account_id={0}".format(account_id)
                sql_str += " AND vessel_id NOT IN ('{0}')".format(vessel_ids[0])

            else:

                sql_str += " WHERE account_id={0}".format(account_id)
                sql_str += " AND vessel_id NOT IN {0}".format(tuple(vessel_ids))

            # FETCH ALL
            rows = self.postgres.query_fetch_all(sql_str)

            for row in rows or []:

                conditions = []

                conditions.append({
                    "col": "vessel_id",
                    "con": "=",
                    "val": row['vessel_id']
                    })

                conditions.append({
                    "col": "account_id",
                    "con": "=",
                    "val": account_id
                    })

                account_vessel_data = {}
                account_vessel_data['vessel_vpn_state'] = 'pending'
                account_vessel_data['allow_access'] = False
                self.postgres.update('account_vessel', account_vessel_data, conditions)

            # RETURN
            return 1

        return 0
