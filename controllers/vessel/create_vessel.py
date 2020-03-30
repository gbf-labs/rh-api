# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, too-many-locals, too-many-arguments, too-many-statements, too-many-instance-attributes, bare-except
""" CREATE VESSEL """
import time
import json
from configparser import ConfigParser
import requests
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class CreateVessel(Common):
    """Class for CreateVessel"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Invite class"""

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.postgres = PostgreSQL()

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(CreateVessel, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    # GET VESSEL FUNCTION
    def create_vessel(self):
        """
        This API is for create vessel
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
          - name: userid
            in: header
            description: User ID
            required: true
            type: string
          - name: query
            in: body
            description: Create Vessel
            required: true
            schema:
              id: Create Vessel
              properties:
                imo:
                    type: string
                vessel_name:
                    type: string
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
        imo = query_json["imo"]
        vessel_name = query_json["vessel_name"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)


        if self.vpn_db_build.upper() == 'TRUE':

            callback_url = self.my_protocol + "://" + self.my_ip + "/vessels/vpn/update"
            job_id = self.insert_job(callback_url, imo, vessel_name)

            # INIT PARAMS FOR CREATE VPN
            vpn_params = {}
            vpn_params['callback_url'] = callback_url
            vpn_params['job_id'] = job_id
            vpn_params['vessel_name'] = vessel_name
            vpn_params['vessel_number'] = imo

            # CREATE VPN
            if not self.create_vpn(vpn_params):

                data["alert"] = "Please try again after 5 minutes!"
                data['status'] = 'Failed'

                # RETURN ALERT
                return self.return_data(data)

        vess = {}
        vess['number'] = imo
        vess['vessel_id'] = imo
        vess['vessel_name'] = vessel_name
        vess['update_on'] = time.time()
        vess['created_on'] = time.time()

        self.postgres.insert('vessel', vess)

        data['message'] = "Vessel VPN successfully created!"
        data['status'] = "ok"

        return self.return_data(data)

    def insert_job(self, callback_url, imo, vessel_name):
        """Insert Job"""

        update_on = time.time()

        # INIT NEW JOB
        temp = {}
        temp['imo'] = imo
        temp['vessel_name'] = vessel_name
        temp['callback_url'] = callback_url
        temp['token'] = self.vpn_token
        temp['status'] = 'pending'
        temp['vpn_type'] = 'VESSEL'
        temp['action'] = 'CREATE'
        temp['update_on'] = update_on
        temp['created_on'] = update_on

        # INSERT NEW JOB
        job_id = self.postgres.insert('vessel_vpn_job',
                                      temp,
                                      'vessel_vpn_job_id'
                                     )

        return job_id

    def create_vpn(self, data):
        """Create VPN"""

        try:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/vessel/vpn"

            headers = {'content-type': 'application/json', 'token': self.vpn_token}

            req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
            res = req.json()

            return res

        except:

            return 0
