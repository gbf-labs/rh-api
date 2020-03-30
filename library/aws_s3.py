# pylint: disable=too-many-locals, no-member
""" AWS S3 """
from configparser import ConfigParser
import boto3
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.config_parser import config_section_parser

class AwsS3(Common):
    """Class for AwsS3"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for S3 class"""
        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        super(AwsS3, self).__init__()

    def get_vessel_image(self, vessel_id):
        """ Return Vessel Image URL"""

        assert vessel_id, "Vessel ID is required."

        # DATA
        sql_str = "SELECT * FROM vessel_image"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND status = 'active'"

        vessel = self.postgres.query_fetch_one(sql_str)

        image_url = ""
        if vessel:
            filename = vessel['image_name']
            ext = filename.split(".")[-1]

            # IMAGE FILE NAME
            image_name = str(vessel['vessel_image_id']) + "." + ext
            key_file = 'Vessel/' + "RH_" + vessel['vessel_imo'] + "_" + image_name

            image_url = self.get_url(key_file)

        return image_url


    def get_vessel_file(self, vessel_id, file_name):
        """ Return Vessel File URL"""

        assert vessel_id, "Vessel ID is required."

        # DATA
        sql_str = "SELECT * FROM vessel_file"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND file_name ='{0}'".format(file_name)
        sql_str += " AND status = 'active'"

        vessel = self.postgres.query_fetch_one(sql_str)

        url = ""
        if vessel:
            filename = vessel['file_name']
            # ext = filename.split(".")[-1]

            # IMAGE FILE NAME
            # fname = str(vessel['vessel_file_id']) + "." + ext
            # key_file = 'VesselFiles/' + "RH_" + vessel['vessel_imo'] + "_" + fname
            key_file = 'VesselFiles/' +  vessel['vessel_imo'] + "/" + filename

            url = self.get_url(key_file)

        return url

    def get_url(self, key):
        """ Return S3 URL """
        assert key, "Key is required."
        # AWS ACCESS
        aws_access_key_id = config_section_parser(self.config, "AWS")['aws_access_key_id']
        aws_secret_access_key = config_section_parser(self.config,
                                                      "AWS")['aws_secret_access_key']
        region_name = config_section_parser(self.config, "AWS")['region_name']

        # CONNECT TO S3
        s3_client = boto3.client('s3',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=region_name)

        s3_params = {
            'Bucket': config_section_parser(self.config, "AWS")['bucket'],
            'Key': key
        }

        expiration = config_section_parser(self.config, "AWS")['image_expires']
        url = s3_client.generate_presigned_url('get_object',
                                               Params=s3_params,
                                               ExpiresIn=expiration,
                                               HttpMethod='GET')
        return url

    def save_file(self, key_file, body_request):
        """ Save File to S3 Bucket """

        # AWS ACCESS
        aws_access_key_id = config_section_parser(self.config, "AWS")['aws_access_key_id']
        aws_secret_access_key = config_section_parser(self.config,
                                                      "AWS")['aws_secret_access_key']
        region_name = config_section_parser(self.config, "AWS")['region_name']

        # CONNECT TO S3
        s3_resource = boto3.resource('s3',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=region_name)
        # SAVE TO S3
        save_to_bucket = s3_resource.Bucket('rh.fileserver').put_object(
            Key=key_file,
            Body=body_request)

        if save_to_bucket:
            return 1
        return 0

    def get_device_image(self, vessel_id, device_id):
        """ Return Device Image URL"""

        assert vessel_id, "Vessel ID is required."
        assert device_id, "Device ID is required."

        # DATA
        sql_str = "SELECT * FROM device_image"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        sql_str += " AND device_id='{0}'".format(device_id)
        sql_str += " AND status = 'active'"

        device = self.postgres.query_fetch_one(sql_str)

        image_url = ""
        if device:
            filename = device['image_name']
            ext = filename.split(".")[-1]

            # IMAGE FILE NAME
            image_name = str(device['device_image_id']) + "." + ext
            key_file = 'Device/' + "RH_" + device['vessel_imo'] + "_" + str(device_id) + image_name

            image_url = self.get_url(key_file)

        return image_url
