# pylint: disable=too-many-locals, ungrouped-imports
"""Device Images"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.aws_s3 import AwsS3

class DeviceImages(Common):
    """Class for DeviceImages"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeviceImages class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.aws3 = AwsS3()
        super(DeviceImages, self).__init__()

    def get_images(self):
        """
        This API is for Getting All Vessel Device Images
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
            description: Device Images
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')
        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        device_images = self.get_device_images(vessel_id)

        for d_image in device_images:
            d_image['image_url'] = self.aws3.get_device_image(d_image['vessel_id'],
                                                              d_image['device_id'])

        data['device_images'] = device_images
        data['status'] = 'ok'

        return self.return_data(data)

    def get_device_images(self, vessel_id):
        """Get Device Images"""
        assert vessel_id, "Vessel ID is required."

        sql_str = "SELECT * FROM device_image"
        sql_str += " WHERE vessel_id = '{0}'".format(vessel_id)
        sql_str += " AND status = 'active'"

        device_images = self.postgres.query_fetch_all(sql_str)

        return device_images
