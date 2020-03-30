#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=no-self-use
"""General Info"""
from __future__ import division
import re
from flask import request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common

class GeneralInfo(Common):
    """Class for GeneralInfo"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for GeneralInfo class"""
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.epoch_default = 26763
        super(GeneralInfo, self).__init__()

    def general_info(self):
        """
        This API is for getting general info of device
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
        responses:
          500:
            description: Error
          200:
            description: Vessel Device List
        """
        # INIT DATA
        data = {}

        # VESSEL ID
        vessel_id = request.args.get('vessel_id')

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
            data["alert"] = "No Vessel ID"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        rows = []

        heading = self.get_heading(vessel_id)
        if heading:
            row = {}
            row['option_name'] = 'Heading'
            row['value'] = "{0}°".format(float(heading['heading']))
            row['data_provider'] = heading['heading_source']
            rows.append(row)

        speed = self.get_speed(vessel_id)
        if speed:
            row = {}
            row['option_name'] = 'Speed'
            row['value'] = speed['speed']
            row['data_provider'] = speed['speed_source']
            rows.append(row)

        failover = self.couch_query.get_complete_values(
            vessel_id,
            "FAILOVER"
        )

        if failover:
            row = {}
            row['option_name'] = 'Internet provider'
            row['value'] = failover['FAILOVER']['General']['Description']
            row['data_provider'] = 'Failover'
            rows.append(row)

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        info = parameters['PARAMETERS']['INFO']
        if info:
            row = {}
            row['option_name'] = 'IMO'
            row['value'] = info['IMO']
            row['data_provider'] = 'PARAMETERS'
            rows.append(row)

        if info:
            row = {}
            row['option_name'] = 'MMSI'
            row['value'] = info['MMSI']
            row['data_provider'] = 'PARAMETERS'
            rows.append(row)

        data['status'] = 'ok'
        data['rows'] = rows
        return self.return_data(data)

    def get_heading(self, vessel_id):
        """Return Heading"""

        all_devices = self.couch_query.get_all_devices(vessel_id)

        source = 'VSAT'
        devices = self.get_device(all_devices, source)

        data = {}
        for device in devices:

            values = self.couch_query.get_complete_values(
                vessel_id,
                device['device']
            )

            if values:

                # GET DEVICE NUMBER
                number = device['device'].split(source)[1]

                # GET DEVICE COMPLETE NAME
                heading_source = self.device_complete_name(source, number)

                # SET RETURN

                data['heading'] = values[device['device']]['General']['Heading']
                data['heading_source'] = heading_source

                # # RETURN
                # return data

        source = 'NMEA'
        devices = self.get_device(all_devices, source)

        for device in devices:

            values = self.couch_query.get_complete_values(
                vessel_id,
                device['device']
            )

            if values:

                # GET DEVICE NUMBER
                number = device['device'].split(source)[1]

                # GET DEVICE COMPLETE NAME
                heading_source = self.device_complete_name(source, number)
                gen = values[device['device']].keys()
                if 'GP0001' in gen:

                    gp0001 = values[device['device']]['GP0001']
                    # SET RETURN

                    if not data:

                        data['heading'] = gp0001['VTG']['courseOverGroundTrueDegrees']
                        data['heading_source'] = heading_source
        # RETURN
        return data

    def get_device(self, devices, pattern):
        """Return Device"""

        data = []
        for device in devices:

            if re.findall(r'' + pattern + r'\d', device['doc']['device']):
                data.append(device['doc'])

        data = sorted(data, key=lambda i: i['device'])

        return data

    def get_speed(self, vessel_id):
        """Return Speed"""
        all_devices = self.couch_query.get_all_devices(vessel_id)

        source = 'NMEA'
        devices = self.get_device(all_devices, source)

        data = {}
        speed = None
        speed_source = ""
        for device in devices:

            values = self.couch_query.get_complete_values(
                vessel_id,
                device['device']
            )

            if values:

                # GET DEVICE NUMBER
                number = device['device'].split(source)[1]

                # GET DEVICE COMPLETE NAME
                heading_source = self.device_complete_name(source, number)
                gen = values[device['device']].keys()
                if 'GP0001' in gen:


                    gp0001 = values[device['device']]['GP0001']
                    # SET RETURN

                    if not data:

                        data['heading'] = gp0001['VTG']['courseOverGroundTrueDegrees']
                        data['heading_source'] = heading_source

                    speed = float(gp0001['VTG']['speedOverGroundKnots'])
                    speed_source = device['device']

                    data['speed'] = str(speed) + " knot(s)"
                    data['speed_source'] = speed_source

                    return data
        return 0
