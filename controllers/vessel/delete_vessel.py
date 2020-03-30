# pylint: disable=too-many-instance-attributes
"""Delete Vessel"""
# coding: utf-8
# pylint: disable=bare-except
import os
import json
import subprocess
from configparser import ConfigParser
import requests

from flask import  request
from library.common import Common
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser

class DeleteVessel(Common):
    """Class for DeleteVessel"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeleteVessel class"""
        super(DeleteVessel, self).__init__()

        self.couch_query = Queries()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.postgres = PostgreSQL()

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    def delete_vessel(self):
        """
        This API is for Deleting Permission
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
            description: Vessel infos
            required: true
            schema:
              id: Delete Vessels
              properties:
                vessel_info:
                    types: array
                    example: [{'vessel_id': vesselid1,
                               'vessel_rev': vesselrev1
                              }]
        responses:
          500:
            description: Error
          200:
            description: Delete Vessel
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # GET QUERY
        vessel_info = query_json["vessel_info"]

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        for vssl in vessel_info:

            doc = self.couch_query.get_by_id(vssl['vessel_id'])

            # INIT PARAMS FOR CREATE VPN
            vpn_params = {}

            vpn_params['vessel_number'] = vssl['vessel_id']
            if 'error' not in doc.keys():

                vpn_params['vessel_number'] = doc['number']

            if self.vpn_db_build.upper() == 'TRUE':

                if not self.revoke_vpn(vpn_params):

                    data["alert"] = "Please try again after 5 minutes!"
                    data['status'] = 'Failed'

                    # RETURN ALERT
                    return self.return_data(data)

            vessel_id = vssl['vessel_id']
            vessel_rev = vssl['vessel_rev']

            os.path.dirname(os.path.realpath(__file__))
            subprocess.Popen(["nohup", "python3", "delete_vessel.py",
                              str(vessel_id), str(vessel_rev), ">", "out.log", "&"])

        data['message'] = "Vessel(s) successfully Deleted!"
        data['status'] = "ok"
        return self.return_data(data)

    def revoke_vpn(self, data):
        """Update VPN"""

        try:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/delete/vessel/vpn"

            headers = {'content-type': 'application/json', 'token': self.vpn_token}

            req = requests.delete(api_endpoint, data=json.dumps(data), headers=headers)
            res = req.json()

            if res['status'] == 'ok':

                cmd = "rm -rf /home/admin/all_vpn/VESSEL_" + str(data['vessel_number']) + ".zip"
                _ = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, check=True)

            return res

        except:

            return 0
