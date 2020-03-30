# pylint: disable=too-many-instance-attributes
""" RC System"""
import json
from configparser import ConfigParser
import requests
from flask import  request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class RCSystem(Common):
    """Class for RCSystem"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for RCSystem class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']

        self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
        self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

        self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'
        super(RCSystem, self).__init__()

    # GET VESSEL FUNCTION
    def rc_system(self):
        """
        This API is for Remote Command
        ---
        tags:
          - Remote Command
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
            description: Remote Command System
            required: true
            schema:
              id: Remote Command System
              properties:
                label:
                    type: string
                key:
                    type: string
                vessel_id:
                    type: string
                others:
                    type: json
                    example: {}
        responses:
          500:
            description: Error
          200:
            description: Remote Command
        """
        # INIT DATA
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        remote_addr = request.remote_addr

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if self.vpn_db_build.upper() == 'False':
            data["alert"] = "Not accessible here!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        vessel_id = query_json['vessel_id']

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        ntwconf = self.couch_query.get_complete_values(
            vessel_id,
            "NTWCONF"
        )

        params = {}
        params['host'] = ntwconf['NTWCONF']['tun1']['IP']
        params['port'] = 22
        params['user'] = parameters['PARAMETERS']['DBOBU']['USER']
        params['password'] = parameters['PARAMETERS']['DBOBU']['PASS']
        params['key'] = query_json['key']
        params['label'] = query_json['label']
        params['remote_addr'] = remote_addr

        if 'others' in query_json.keys():
            params['others'] = query_json['others']

        # SEND COMMAND
        output = self.send_command(params)

        data = {}
        if output['status'] == 'failed':
            # print("Params: ", params)

            data['status'] = "failed"
            data['alert'] = "Can\'t connect to vessel server!"
            return self.return_data(data)

        data['output'] = output['output']
        data['command_info'] = output['command_info']
        data['connection_info'] = output['connection_info']
        data['status'] = "ok"

        return self.return_data(data)

    def send_command(self, data):
        """Send Command"""

        api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/remote/command"

        headers = {'content-type': 'application/json', 'token': self.vpn_token}
        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res
