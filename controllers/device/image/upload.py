# pylint: disable=no-member, too-many-locals, no-self-use, too-many-statements
#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
"""Device Image Upload """
import time

from flask import request
# from library.couch_database import CouchDatabase
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.common import Common
from library.aws_s3 import AwsS3

class Upload(Common):
    """Class for Device Upload"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Device Upload class"""
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.aws3 = AwsS3()

        super(Upload, self).__init__()

    # GET VESSEL FUNCTION
    def device_upload(self):
        """
        This API is for Device Image Upload
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
          - name: device_id
            in: query
            description: Device ID
            required: true
            type: string
          - name: upfile
            in: formData
            description: Device image
            required: true
            type: file
        consumes:
          - multipart/form-data
        responses:
          500:
            description: Error
          200:
            description: Device Image Upload
        """
        # INIT DATA
        data = {}

        # VESSEL ID
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')

        # # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # RH_<VesselIMO>_<ImageID>

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )


        # VESSEL IMO
        vessel_imo = vessel_id
        if parameters:
            vessel_imo = parameters['PARAMETERS']['INFO']['IMO']

        try:

            filename = request.files['upfile'].filename
            ext = filename.split(".")[-1]

            if not self.allowed_image_type(filename):

                data["alert"] = "File Type Not Allowed!"
                data['status'] = 'Failed'
                return self.return_data(data)

        except ImportError:
            data["alert"] = "No image!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        filename = self.rename_device_image(vessel_id, device_id, filename)

        dimg_data = {}
        dimg_data['vessel_id'] = vessel_id
        dimg_data['device_id'] = device_id
        dimg_data['vessel_imo'] = vessel_imo
        dimg_data['image_name'] = filename
        dimg_data['status'] = "active"
        dimg_data['created_on'] = time.time()

        # VERIFY IF IMAGE EXISTS FOR DEVICE
        sql_str = "SELECT * FROM device_image"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND device_id='{0}'".format(device_id)
        sql_str += " AND status = 'active'"

        device = self.postgres.query_fetch_one(sql_str)

        if device:

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "device_image_id",
                "con": "=",
                "val": device['device_image_id']
                })

            update_column = {}
            update_column['status'] = "inactive"

            self.postgres.update('device_image', update_column, conditions)

        device_image_id = self.postgres.insert('device_image', dimg_data, 'device_image_id')

        # IMAGE FILE NAME
        file_name = vessel_imo + "_" + str(device_id) + str(device_image_id) + "." + ext
        img_file = 'Device/' + "RH_" + str(file_name)
        body = request.files['upfile']

        # SAVE TO S3
        image_url = ""
        if self.aws3.save_file(img_file, body):
            image_url = self.aws3.get_url(img_file)

        data["status"] = "ok"
        data["image_url"] = image_url

        # RETURN
        return self.return_data(data)

    def allowed_image_type(self, filename):
        """ Check Allowed File Extension """

        allowed_extensions = set(['png', 'jpg', 'jpeg', 'gif'])

        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    def rename_device_image(self, vessel_id, device_id, filename):
        """Rename Image"""

        sql_str = "SELECT * FROM device_image"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND device_id='{0}'".format(device_id)
        sql_str += " AND image_name='{0}'".format(filename)

        device_image = self.postgres.query_fetch_one(sql_str)

        if device_image:
            new_name = self.file_replace(device_image['image_name'])

            return self.rename_device_image(vessel_id, device_id, new_name)

        return filename
