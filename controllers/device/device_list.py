# pylint: disable=too-many-locals, ungrouped-imports
"""Device List"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.aws_s3 import AwsS3

class DeviceList(Common):
    """Class for DeviceImages"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeviceImages class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.aws3 = AwsS3()
        super(DeviceList, self).__init__()

    def get_list(self):
        """
        This API is for Getting All Vessel Device List
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
            description: Vessel Device List
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # COUNT
        sql_str = "SELECT COUNT(*) FROM vessel"

        count = self.postgres.query_fetch_one(sql_str)
        total_rows = count['count']

        offset = int((page - 1) * limit)

        # DATA
        sql_str = "SELECT * FROM vessel LIMIT {0} OFFSET {1} ".format(limit, offset)
        vessels = self.postgres.query_fetch_all(sql_str)

        rows = []
        if vessels:

            vessel_ids = [x['vessel_id'] for x in vessels]

            for vessel_id in vessel_ids:

                vessel_name = self.get_vessel_name(vessel_id)
                devices = self.get_vessel_devices(vessel_id)

                rows.append({
                    "vessel_id": vessel_id,
                    "vessel_name": vessel_name,
                    "devices": devices
                })

        total_page = int(math.ceil(int(total_rows - 1) / limit)) + 1

        data['data'] = rows
        data['total_page'] = total_page
        data['limit'] = int(limit)
        data['page'] = int(page)
        data['total_rows'] = total_rows
        data['status'] = 'ok'

        return self.return_data(data)

    def get_vessel_name(self, vessel_id):
        """ Return Vessel Name """

        assert vessel_id, "Vessel ID is required."
        values = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        if values:
            vessel_name = values['PARAMETERS']['INFO']['VESSELNAME']
        else:

            sql_str = "SELECT vessel_name FROM vessel WHERE vessel_id='{0}'".format(vessel_id)
            vname = self.postgres.query_fetch_one(sql_str)
            vessel_name = ""
            if vname:
                vessel_name = vname['vessel_name']

        return vessel_name

    def get_vessel_devices(self, vessel_id):
        """ Return Vessel Devices """
        assert vessel_id, "Vessel ID is required."

        sql_str = "SELECT device_id, device FROM device"
        sql_str += " WHERE vessel_id = '{0}'".format(vessel_id)
        sql_str += " AND device NOT IN ('PARAMETERS', 'COREVALUES',"
        sql_str += " 'FAILOVER', 'NTWCONF', 'NTWPERF1')"

        devices = self.postgres.query_fetch_all(sql_str)

        if devices:
            for device in devices:
                device['image_url'] = self.aws3.get_device_image(vessel_id,
                                                                 device['device_id'])
        return devices
