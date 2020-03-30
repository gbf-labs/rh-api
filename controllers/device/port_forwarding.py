#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=too-many-locals, too-many-statements, too-few-public-methods
"""Port Forwarding"""
import math

from flask import request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common

class PortForwarding(Common):
    """Class for PortForwarding"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for PortForwarding class"""
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.epoch_default = 26763
        super(PortForwarding, self).__init__()

    def port_forwarding(self):

        """
        This API is for getting Port Forwarding of device
        ---
        tags:
          - Devices
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
          - name: vessel_id
            in: query
            description: Vessel ID
            required: true
            type: string
          - name: device_id
            in: query
            description: Device ID
            required: false
            type: string
          - name: limit
            in: query
            description: Limit
            required: true
            type: integer
          - name: page
            in: query
            description: Page
            required: true
            type: integer
        responses:
          500:
            description: Error
          200:
            description: Vessel Device Info
        """

        data = {}

        # VESSEL ID
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not vessel_id:
            data["alert"] = "Please complete parameters!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # device_list = []
        device_name = ""
        if device_id:

            device_data = self.couch_query.get_by_id(device_id)
            dev_name = device_data['device']
            # device_list.append(value)

        # else:

        #     device_list = self.couch_query.get_device(vessel_id)

        # REMOVE DATA
        # data_to_remove = ['PARAMETERS', 'COREVALUES', 'FAILOVER', 'NTWCONF', 'NTWPERF1']
        # device_list = self.remove_data(device_list, data_to_remove)

        datas = {}
        datas['data'] = []
        final_data = []

        ntwconf = self.couch_query.get_complete_values(
            vessel_id,
            "NTWCONF"
        )

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        vpn_ip = ntwconf['NTWCONF']['tun1']['IP']

        keys = parameters['PARAMETERS'].keys()
        for i in range(1, (len(keys))):
            temp_pf = {}
            port = 'PORTFORWARDING' + str(i)
            if port in keys:

                destination_ip_val = parameters['PARAMETERS'][port]['DESTINATIONIP']
                destination_port_val = parameters['PARAMETERS'][port]['DESTINATIONPORT']
                description_val = parameters['PARAMETERS'][port]['DESCRIPTION']
                device_name = parameters['PARAMETERS'][port]['DEVICE']

                link = description_val.lower() + '://'
                link += vpn_ip + ':' + parameters['PARAMETERS'][port]['SOURCEPORT']

                if device_id and dev_name == device_name:

                    temp_pf['destination_ip'] = destination_ip_val
                    temp_pf['destination_port'] = destination_port_val
                    temp_pf['description'] = description_val
                    temp_pf['link'] = link
                    temp_pf['device'] = device_name

                    final_data.append(temp_pf)

                elif not device_id:

                    temp_pf['destination_ip'] = destination_ip_val
                    temp_pf['destination_port'] = destination_port_val
                    temp_pf['description'] = description_val
                    temp_pf['link'] = link
                    temp_pf['device'] = device_name

                    final_data.append(temp_pf)

        total_count = len(final_data) - 1
        total_page = int(math.ceil(int(total_count) / limit)) + 1
        final_data = self.limits(final_data, limit, page)

        datas['total_rows'] = total_count + 1
        datas['total_page'] = total_page
        datas['limit'] = int(limit)
        datas['page'] = int(page)
        datas['data'] = final_data
        datas['status'] = 'ok'

        return self.return_data(datas)
