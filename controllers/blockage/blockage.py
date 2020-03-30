# pylint: disable=too-many-locals, too-many-statements, too-many-arguments, too-many-nested-blocks
"""Blockage"""
import time
from datetime import date
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.blockages import Blockages

class Blockage(Common):
    """Class for Blockage"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Blockage class"""
        self.blocks = Blockages()
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(Blockage, self).__init__()

    def blockage(self):
        """
        This API is for Getting Blockage Data
        ---
        tags:
          - Blockage
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
            types: string
          - name: device_id
            in: query
            description: Device ID
            required: true
            types: string
          - name: start_time
            in: query
            description: Epoch start
            required: true
            type: string
          - name: end_time
            in: query
            description: Epoch end
            required: true
            type: string
        responses:
          500:
            description: Error
          200:
            description: Blockage Map
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        device = self.get_device_type(vessel_id, device_id)

        if not device:
            data["alert"] = "No Vessel/Device found"
            data['status'] = 'Failed'
            return self.return_data(data)

        device_type = device['device_type']
        device = device['device']

        map_available = self.blocks.allowed_device_type(device_type)

        if not map_available:

            data["alert"] = "Map not available to device."
            data['status'] = 'Failed'
            return self.return_data(data)

        # CHECK DATE TIME IF < TODAY
        start = time.strftime('%Y-%m-%d', time.localtime(float(start_time)))
        current_date = str(date.today())

        antenna_status = []
        block_zone = []
        coordinates = {}

        if start == current_date:

            device_data = self.get_current_blockage(vessel_id, device, device_type,
                                                    str(start_time), str(end_time))
            if device_data:
                block_zone = device_data['block_zone']
                coordinates = device_data['coordinates']
                antenna_status = device_data['antenna_status']
        else:

            search_start = self.epoch_day(round(float(start_time)))
            search_end = self.epoch_day(round(float(end_time)))
            datas = self.get_blockage_data(vessel_id, device_id, int(search_start), int(search_end))

            if datas:

                # GET ANTENNA STATUS
                astatus = [data['antenna_status'] for data in datas]
                # antenna = set([stat for stat in astatus for stat in stat])
                antenna = {stat for stat in astatus for stat in stat}
                antenna_status = self.blocks.antenna_status(antenna)

                block_zone = self.get_blockzones(vessel_id, device_id, start_time, end_time)
                coordinates = self.blocks.get_xydata(datas, antenna, start_time,
                                                     end_time, remarks='merge')

            # ADDING COUCH DATA IF DATE SELECTION IS CURRENT TIMESTAMP
            end = time.strftime('%Y-%m-%d', time.localtime(float(end_time)))
            if end == current_date:

                start_today = self.epoch_day(end_time)

                current_coords = self.get_current_blockage(vessel_id, device, device_type,
                                                           str(start_today), str(end_time))
                if current_coords:

                    for stat in current_coords['coordinates']:
                        if stat in coordinates:

                            coordinates[stat]['coordinates'].extend(
                                current_coords['coordinates'][stat]['coordinates'])
                        else:

                            coordinates.update({stat: current_coords['coordinates'][stat]})

        # CURRENT POSITION
        current_position = self.blocks.get_current_position(vessel_id, device)
        zone_number = self.blocks.get_zone_number(device_type)

        data['blockage'] = block_zone
        data['blockzone_number'] = zone_number
        data['current_position'] = current_position
        data['coordinates'] = coordinates
        data['antenna_status'] = antenna_status
        data['map_available'] = map_available
        data['status'] = 'ok'

        return self.return_data(data)

    # GET ALARM TRIGGER
    def get_device_type(self, vessel_id, device_id):
        """Get Device Type"""

        assert device_id, "Device ID is required."

        # DATA
        sql_str = "SELECT * FROM device "
        sql_str += "WHERE vessel_id='{0}' ".format(vessel_id)
        sql_str += "AND device_id='{0}'".format(device_id)
        device = self.postgres.query_fetch_one(sql_str)

        return device

    def get_blockage_data(self, vessel_id, device_id, start, end):
        """ RETURN ALL BLOCKAGE DATA BY DATE RANGE"""

        sql_str = "SELECT * FROM blockage_data "
        sql_str += "WHERE vessel_id='{0}' ".format(vessel_id)
        sql_str += "AND device_id='{0}' ".format(device_id)
        sql_str += "AND epoch_date "
        sql_str += "BETWEEN '{0}' AND '{1}' ".format(start, end)
        sql_str += "ORDER BY epoch_date DESC"
        datas = self.postgres.query_fetch_all(sql_str)

        return datas

    def get_blockzones(self, vessel_id, device_id, start, end):
        """ Return Blockage Zones """

        sql_str = "SELECT DISTINCT blockzones FROM blockage_data "
        sql_str += "WHERE vessel_id='{0}' ".format(vessel_id)
        sql_str += "AND device_id='{0}' ".format(device_id)
        sql_str += "AND epoch_date "
        sql_str += "BETWEEN '{0}' AND '{1}' ".format(str(start), str(end))

        datas = self.postgres.query_fetch_all(sql_str)
        blockzones = []
        if datas:

            for data in datas:

                blockzones.append(data['blockzones'][0])

        return blockzones

    def get_current_blockage(self, vessel_id, device, device_type, start_time, end_time):
        """ Return Current Blockage Data """

        data = {}
        device_data = self.blocks.get_device_data(vessel_id, device,
                                                  start_time, str(end_time))
        if device_data:
            blockage = self.blocks.get_blockage_data(device, device_data)
            data['block_zone'] = self.blocks.get_blockage_zones(device, device_type, device_data)

            # GET ANTENNA STATUS
            antenna = set(data['antenna_status'] for data in blockage)
            data['antenna_status'] = self.blocks.antenna_status(antenna)
            data['coordinates'] = self.blocks.get_xydata(blockage, antenna, 0, 0, remarks='format')

        return data
