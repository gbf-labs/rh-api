# pylint: disable=too-many-locals, too-many-statements, too-many-instance-attributes, too-many-branches
"""VPN Data"""
from configparser import ConfigParser
from flask import request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.config_parser import config_section_parser

class VPNData(Common):
    """Class for VPNData"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for VPNData class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()

        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(VPNData, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    def vpn_data(self):
        """
        This API is for Getting Data for VPN
        ---
        tags:
          - VPN
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: jobid
            in: header
            description: Job ID
            required: true
            type: string

        responses:
          500:
            description: Error
          200:
            description: Role
        """
        data = {}

        # GET DATA
        job_id = request.headers.get('jobid')
        token = request.headers.get('token')

        # CHECK TOKEN
        datas = self.validate_job_id_token(job_id, token)

        if not datas['data']:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # datas['data']['vpn_type'] ='CLIENT'
        # datas['data']['account_os'] ='WINDOWS' # LINUX
        # datas['data']['action'] ='CREATE'

        datas['status'] = 'ok'

        return self.return_data(datas)

    def validate_job_id_token(self, job_id, token):
        """Validate Job ID Token"""

        # print("*"*50," vpn_data ", "*"*50)
        # print("job_id: ", job_id)
        # print("token: ", token)
        # print("*"*50, " vpn_data ", "*"*50)

        sql_str = "SELECT * FROM job WHERE job_id={0} AND token='{1}'".format(job_id, token)
        job = self.postgres.query_fetch_one(sql_str)

        data = {}
        data['data'] = None

        if job:

            vessel_ips = []
            account_ip_address = None

            sql_str = "SELECT username FROM account WHERE id={0}".format(job['account_id'])
            account = self.postgres.query_fetch_one(sql_str)

            if account:
                job['account_name'] = account['username']
                data['data'] = job

            if job['action'] == 'ADD':

                sql_str = "SELECT a.id, a.status FROM account a INNER JOIN job j"
                sql_str += " ON a.id=j.account_id WHERE j.job_id={0}".format(job_id)
                account = self.postgres.query_fetch_one(sql_str)
                account_id = account['id']
                account_status = account['status']

                sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
                sql_str += "AND role_id in (SELECT role_id FROM role "
                sql_str += "WHERE role_name='super admin')"

                super_admin = self.postgres.query_fetch_one(sql_str)

                vpn_type = 'VCLIENT'

                if super_admin:

                    vpn_type = 'VRH'

                # INIT SQL QUERY
                sql_str = "SELECT vpn_ip FROM account_vpn WHERE "
                sql_str += "vpn_type='{0}' AND account_id='{1}' ".format(vpn_type, account_id)
                sql_str += "AND status = true ORDER BY created_on DESC"

                account_vpn = self.postgres.query_fetch_one(sql_str)
                account_ip_address = account_vpn['vpn_ip']

                sql_str = ""
                if account_status:

                    sql_str = "SELECT * FROM account_vessel WHERE account_id={0}".format(account_id)

                else:

                    sql_str = "SELECT * FROM account_offline_vessel"
                    sql_str += " WHERE account_id={0}".format(account_id)

                vessels = self.postgres.query_fetch_all(sql_str)

                for vessel in vessels:

                    if vessel['allow_access']:

                        parameters = self.couch_query.get_complete_values(
                            vessel['vessel_id'],
                            "PARAMETERS"
                        )

                        ntwconf = self.couch_query.get_complete_values(
                            vessel['vessel_id'],
                            "NTWCONF"
                        )
                        temp = {}
                        temp['ip'] = ntwconf['NTWCONF']['tun1']['IP']
                        temp['port'] = '22'
                        temp['username'] = parameters['PARAMETERS']['DBOBU']['USER']
                        temp['password'] = parameters['PARAMETERS']['DBOBU']['PASS']
                        temp['vessel_name'] = parameters['PARAMETERS']['INFO']['VESSELNAME']
                        temp['imo'] = parameters['PARAMETERS']['INFO']['IMO']

                        vessel_ips.append(temp)

            elif job['action'] == 'REMOVE':

                sql_str = "SELECT a.id, a.status FROM account a INNER JOIN job j"
                sql_str += " ON a.id=j.account_id WHERE j.job_id={0}".format(job_id)
                account = self.postgres.query_fetch_one(sql_str)
                account_id = account['id']
                account_status = account['status']

                sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
                sql_str += "AND role_id in (SELECT role_id FROM role "
                sql_str += "WHERE role_name='super admin')"

                super_admin = self.postgres.query_fetch_one(sql_str)

                vpn_type = 'VCLIENT'

                if super_admin:

                    vpn_type = 'VRH'

                sql_str = ""
                if account_status:

                    # INIT SQL QUERY
                    sql_str = "SELECT vpn_ip FROM account_vpn WHERE "
                    sql_str += "vpn_type='{0}' AND account_id='{1}' ".format(vpn_type, account_id)
                    sql_str += "AND status = true ORDER BY created_on DESC"

                else:

                    # INIT SQL QUERY
                    sql_str = "SELECT vpn_ip FROM account_vpn WHERE "
                    sql_str += "vpn_type='{0}' AND account_id='{1}' ".format(vpn_type, account_id)
                    sql_str += "AND status = false ORDER BY created_on DESC"

                account_vpn = self.postgres.query_fetch_one(sql_str)
                # print("-"*100)
                # print(account_vpn)
                # print("-"*100)

                if account_vpn:

                    account_ip_address = account_vpn['vpn_ip']

                    sql_str = ""
                    # print("-"*100)
                    # print("account_status: ", account_status)
                    # print("-"*100)
                    if account_status:

                        sql_str = "SELECT * FROM account_vessel"
                        sql_str += " WHERE account_id={0}".format(account_id)

                    else:

                        sql_str = "SELECT * FROM account_offline_vessel"
                        sql_str += " WHERE account_id={0}".format(account_id)

                    vessels = self.postgres.query_fetch_all(sql_str)

                    for vessel in vessels:

                        if not vessel['allow_access']:

                            parameters = self.couch_query.get_complete_values(
                                vessel['vessel_id'],
                                "PARAMETERS"
                            )

                            ntwconf = self.couch_query.get_complete_values(
                                vessel['vessel_id'],
                                "NTWCONF"
                            )
                            temp = {}
                            temp['ip'] = ntwconf['NTWCONF']['tun1']['IP']
                            temp['port'] = '22'
                            temp['username'] = parameters['PARAMETERS']['DBOBU']['USER']
                            temp['password'] = parameters['PARAMETERS']['DBOBU']['PASS']
                            temp['vessel_name'] = parameters['PARAMETERS']['INFO']['VESSELNAME']
                            temp['imo'] = parameters['PARAMETERS']['INFO']['IMO']

                            vessel_ips.append(temp)

                        else:
                            pass
                            # print("*"*100)
                            # print("User don't have IP!, Account ID", account_id)
                            # print("*"*100)
            data['data']['vessel_ips'] = vessel_ips
            data['data']['account_ip_address'] = account_ip_address

        return data
