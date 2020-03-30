# pylint: disable=too-many-locals, ungrouped-imports
"""Vessel Files"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from controllers.cron.update_device_state import UpdateDeviceState
from library.aws_s3 import AwsS3

class VesselFiles(Common):
    """Class for VesselFiles"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for VesselFiles class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.device_state = UpdateDeviceState()
        self.aws3 = AwsS3()
        super(VesselFiles, self).__init__()

    def get_files(self):
        """
        This API is for Getting All Vessel Files
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
          - name: vessel_id
            in: query
            description: Vessel ID
            required: true
            type: string
        responses:
          500:
            description: Error
          200:
            description: Vessel Files
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

        vessel_images = self.get_vessel_images(vessel_id)

        for vimage in vessel_images:
            vimage['image_url'] = self.aws3.get_vessel_image(vimage['vessel_id'])

        vessel_files = self.get_vessel_files(vessel_id)
        for vfile in vessel_files:
            vfile['file_url'] = self.aws3.get_vessel_file(vfile['vessel_id'], vfile['file_name'])

        data['vessel_files'] = vessel_files
        data['vessel_images'] = vessel_images
        data['status'] = 'ok'

        return self.return_data(data)

    def get_vessel_images(self, vessel_id):
        """Get Vessel Images"""
        assert vessel_id, "Vessel ID is required."

        sql_str = "SELECT * FROM vessel_image"
        sql_str += " WHERE vessel_id = '{0}'".format(vessel_id)
        sql_str += " AND status = 'active'"

        vessel_images = self.postgres.query_fetch_all(sql_str)

        return vessel_images

    def get_vessel_files(self, vessel_id):
        """Get Vessel Images"""
        assert vessel_id, "Vessel ID is required."

        sql_str = "SELECT * FROM vessel_file"
        sql_str += " WHERE vessel_id = '{0}'".format(vessel_id)
        sql_str += " AND status = 'active'"

        vessel_files = self.postgres.query_fetch_all(sql_str)

        return vessel_files
