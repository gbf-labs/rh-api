# pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-instance-attributes, too-many-branches, no-member, no-name-in-module, anomalous-backslash-in-string, too-many-function-args, no-self-use
"""VPN Update"""
import time
import urllib.request
from configparser import ConfigParser
from flask import  request
from library.common import Common
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class VesselVPNUpdate(Common):
    """Class for VPNUpdate"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for VPNUpdate class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()

        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(VesselVPNUpdate, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    def vessel_vpn_update(self):
        """
        This API is for Getting Data for VPN
        ---
        tags:
          - Vessel
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
          - name: query
            in: body
            description: Updating VNP
            required: true
            schema:
              id: Updating VNP
              properties:
                status:
                    type: string
                message:
                    type: string
                directory:
                    type: string
                action:
                    type: string
                ip:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Role
        """
        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET DATA
        job_id = request.headers.get('jobid')
        token = request.headers.get('token')

        print("="*50, " vessel_vpn_update ", "="*50)
        print("job_id: ", job_id)
        print("token: ", token)
        print("query_json: ", query_json)
        print("="*50, " vessel_vpn_update ", "="*50)

        vnp_server_ip = query_json['ip']
        action = query_json['action']
        message = query_json['message']
        directory = query_json['directory']
        status = query_json['status']
        created_on = int(time.time())

        filename = directory.split("/")[-1]
        url = self.my_protocol + '://' + self.vessel_vpn + '/zip_vpn/' + filename

        vpn_dir = '/home/admin/all_vpn/' + filename

        urllib.request.urlretrieve(url, vpn_dir)

        # VESSEL VPN
        created_vpn = str(created_on) + "_" + filename
        vvpn_dir = '/home/admin/all_vpn/VESSEL_VPN/' + created_vpn

        urllib.request.urlretrieve(url, vvpn_dir)

        # UPDATE VESSEL VPN JOB
        conditions = []

        conditions.append({
            "col": "token",
            "con": "=",
            "val": str(token)
            })

        conditions.append({
            "col": "vessel_vpn_job_id",
            "con": "=",
            "val": job_id
            })

        vv_job = {}
        vv_job['message'] = message
        vv_job['directory'] = directory
        vv_job['vnp_server_ip'] = vnp_server_ip
        vv_job['status'] = status
        vv_job['action'] = action
        vv_job['created_on'] = created_on

        data = {}
        if self.postgres.update('vessel_vpn_job', vv_job, conditions):

            data['message'] = "Job successfully updated!"
            data['status'] = "ok"

        else:

            data['message'] = "Invalid query!"
            data['status'] = "Failed"

        return self.return_data(data)
