# pylint: disable=no-member, too-many-locals, no-self-use
"""Vessels File Upload """
import time
from flask import request
# from library.couch_database import CouchDatabase
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.common import Common
from library.aws_s3 import AwsS3

class Upload(Common):
    """Class for Vessels"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Vessel Upload class"""
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.aws3 = AwsS3()

        super(Upload, self).__init__()

    # GET VESSEL FUNCTION
    def file_upload(self):
        """
        This API is for Uploading Vessel File
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
            description: Vessel File Upload
        """
        # INIT DATA
        data = {}

        # VESSEL ID
        vessel_id = request.args.get('vessel_id')

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
        vessel_imo = parameters['PARAMETERS']['INFO']['IMO']

        file_upload = []
        filenames = request.files.getlist('upfile')
        for filename in filenames:

            try:

                file_name = filename.filename
                # ext = file_name.split(".")[-1]

                # if not self.allowed_file_type(file_name):

                #     data["alert"] = "File Type Not Allowed!"
                #     data['status'] = 'Failed'
                #     return self.return_data(data)

            except ImportError:

                data["alert"] = "No image!"
                data['status'] = 'Failed'

                # RETURN ALERT
                return self.return_data(data)

            file_name = self.rename_file(vessel_id, file_name)

            vimg_data = {}
            vimg_data['vessel_id'] = vessel_id
            vimg_data['vessel_imo'] = vessel_imo
            vimg_data['file_name'] = file_name
            vimg_data['status'] = "active"
            vimg_data['created_on'] = time.time()

            # ADD FILE TO VESSEL FILE TABLE
            self.postgres.insert('vessel_file', vimg_data, 'vessel_file_id')

            # FILE NAME
            # file_name_upload = str(vessel_file_id) + "." + ext
            # upload_file = 'VesselFiles/' + "RH_" + vessel_imo + "_" + file_name_upload
            upload_file = 'VesselFiles/' + vessel_imo +"/" + file_name
            body = request.files['upfile']

            # SAVE TO S3
            url = ""
            if self.aws3.save_file(upload_file, body):
                url = self.aws3.get_url(upload_file)

            file_upload.append({
                "filename": file_name,
                "url": url
                })

        data["status"] = "ok"
        data["data"] = file_upload

        # RETURN
        return self.return_data(data)

    def allowed_file_type(self, filename):
        """ Check Allowed File Extension """

        allowed_extensions = set(['txt', 'pdf'])

        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    def rename_file(self, vessel_id, filename):
        """ Rename File """
        sql_str = "SELECT * FROM vessel_file"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND file_name='{0}'".format(filename)

        vessel_file = self.postgres.query_fetch_one(sql_str)

        if vessel_file:
            new_name = self.file_replace(vessel_file['file_name'])

            return self.rename_file(vessel_id, new_name)

        return filename
