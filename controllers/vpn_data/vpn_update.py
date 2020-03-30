# pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-instance-attributes, too-many-branches, no-member, no-name-in-module, anomalous-backslash-in-string, too-many-function-args, no-self-use
"""VPN Update"""
import os
import time
import shutil
import urllib.request
import json
from configparser import ConfigParser
import boto3
import requests
from flask import  request
from library.common import Common
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL
from library.emailer import Email
from library.config_parser import config_section_parser
# from templates.message import Message
from templates.vpn_installer import VPNInstallTemp

class VPNUpdate(Common):
    """Class for VPNUpdate"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for VPNUpdate class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()

        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']
        super(VPNUpdate, self).__init__()

        if self.vpn_db_build.upper() == 'TRUE':
            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.my_protocol = config_section_parser(self.config, "IPS")['my_protocol']

            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.user_protocol = config_section_parser(self.config, "IPS")['user_protocol']

            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
            self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

            self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    def vpn_update(self):
        """
        This API is for Getting Data for VPN
        ---
        tags:
          - VPN
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: jobid
            in: header
            description: Job ID
            required: true
            type: string
          - name: query
            in: body
            description: Updating VNP
            required: true
            schema:
              id: Updating VNP
              properties:
                status:
                    type: string
                message:
                    type: string
                directory:
                    type: string
                action:
                    type: string
                ip:
                    type: string
                vpn_type:
                    type: string

        responses:
          500:
            description: Error
          200:
            description: Role
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET DATA
        job_id = request.headers.get('jobid')
        token = request.headers.get('token')

        # print("="*50, " vpn_update ", "="*50)
        # print("job_id: ", job_id)
        # print("token: ", token)
        # print("query_json: ", query_json)
        # print("="*50, " vpn_update ", "="*50)

        ip_address = query_json['ip']
        vpn_type = query_json['vpn_type']
        action = query_json['action']

        datas = self.update_job(job_id, token, query_json)
        # CHECK TOKEN

        if not datas:

            data["alert"] = "Invalid Data!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        # OPEN CONNECTION
        self.postgres.connection()

        if query_json['status'] == 'ok' and action == 'CREATE' and vpn_type in ['CLIENT',
                                                                                'RHADMIN',
                                                                                'VCLIENT',
                                                                                'VRH']:

            if ip_address:

                sql_str = "SELECT a.id FROM account a INNER JOIN job j"
                sql_str += " ON a.id=j.account_id WHERE j.job_id={0}".format(job_id)
                account = self.postgres.query_fetch_one(sql_str)
                account_id = account['id']

                account_vpn_data = {}
                account_vpn_data['account_id'] = account_id
                account_vpn_data['vpn_ip'] = ip_address
                account_vpn_data['status'] = True
                account_vpn_data['vpn_type'] = vpn_type
                account_vpn_data['job_id'] = job_id
                account_vpn_data['created_on'] = time.time()
                self.postgres.insert('account_vpn', account_vpn_data)

        if query_json['status'] == 'ok' and action == 'CREATE' and vpn_type in ['VCLIENT', 'VRH']:

            if ip_address:

                self.postgres.connection()
                sql_str = "SELECT * FROM account_vessel WHERE account_id={0}".format(account_id)
                vessels = self.postgres.query_fetch_all(sql_str)
                self.postgres.close_connection()

                add_ip = False
                remove_ip = False
                for vessel in vessels:

                    add_ip = bool(vessel['allow_access'])

                    if add_ip is True:
                        remove_ip = True
                    # if vessel['allow_access']:
                    #     add_ip = True

                    # else:

                    #     remove_ip = True

                callback_url = self.my_protocol + "://" + self.my_ip + "/vpn/update"
                data_url = self.my_protocol + "://" + self.my_ip + "/vpn/data"

                # OPEN CONNECTION
                self.postgres.connection()

                sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
                sql_str += "AND role_id in (SELECT role_id FROM role "
                sql_str += "WHERE role_name='super admin')"

                super_admin = self.postgres.query_fetch_one(sql_str)

                vpn_type = 'VCLIENT'

                if super_admin:

                    vpn_type = 'VRH'

                # CLOSE CONNECTION
                self.postgres.close_connection()

                sa_role = self.get_sa_role(account_id)

                if add_ip and not sa_role:

                    # INSERT JOB
                    j_id = self.insert_job(callback_url,
                                           data_url,
                                           self.vpn_token,
                                           account_id,
                                           self.vessel_vpn,
                                           'ADD',
                                           vpn_type)

                    # INIT PARAMS FOR CREATE VPN
                    vpn_params = {}
                    vpn_params['callback_url'] = callback_url
                    vpn_params['data_url'] = data_url
                    vpn_params['job_id'] = j_id

                    self.add_vpn_ip(vpn_params, self.vpn_token, True)

                if remove_ip and not sa_role:

                    # INSERT JOB
                    j_id = self.insert_job(callback_url,
                                           data_url,
                                           self.vpn_token,
                                           account_id,
                                           self.vessel_vpn,
                                           'REMOVE',
                                           vpn_type)

                    # INIT PARAMS FOR CREATE VPN
                    vpn_params = {}
                    vpn_params['callback_url'] = callback_url
                    vpn_params['data_url'] = data_url
                    vpn_params['job_id'] = j_id

                    self.add_vpn_ip(vpn_params, self.vpn_token, True)

        elif query_json['status'] == 'ok' and action in ['ADD', 'REMOVE']:

            self.postgres.connection()

            sql_str = "SELECT a.id, a.status FROM account a INNER JOIN job j"
            sql_str += " ON a.id=j.account_id WHERE j.job_id={0}".format(job_id)

            account = self.postgres.query_fetch_one(sql_str)
            self.postgres.close_connection()

            account_id = account['id']
            account_status = account['status']

            conditions = []

            conditions.append({
                "col": "vessel_vpn_ip",
                "con": "=",
                "val": ip_address
                })

            conditions.append({
                "col": "account_id",
                "con": "=",
                "val": account_id
                })

            account_vessel_data = {}
            account_vessel_data['vessel_vpn_state'] = 'ok'

            if account_status:

                self.postgres.update('account_vessel', account_vessel_data, conditions)

            else:

                self.postgres.update('account_offline_vessel', account_vessel_data, conditions)

        elif query_json['status'] == 'DONE' and action in ['DELETE']:

            sql_str = "SELECT a.id FROM account a INNER JOIN job j"
            sql_str += " ON a.id=j.account_id WHERE j.job_id={0}".format(job_id)
            account = self.postgres.query_fetch_one(sql_str)
            account_id = account['id']

            conditions = []

            conditions.append({
                "col": "vpn_type",
                "con": "=",
                "val": vpn_type
                })

            conditions.append({
                "col": "account_id",
                "con": "=",
                "val": account_id
                })

            account_vpn_data = {}
            account_vpn_data['status'] = False
            self.postgres.update('account_vpn', account_vpn_data, conditions)

            self.postgres.connection()

            self.delete_user(job_id, token)

        if query_json['status'] == 'ok' and action == 'CREATE':

            self.send_email_vpn(job_id, token)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        data['message'] = "Job successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_job(self, job_id, token, data):
        """Update Job"""

        conditions = []
        data = self.remove_key(data, "ip")
        data['message'] = self.remove_special_char(data['message'])

        if data['status'] == 'failed':
            data['status'] = 'pending'

        conditions.append({
            "col": "token",
            "con": "=",
            "val": str(token)
            })

        conditions.append({
            "col": "job_id",
            "con": "=",
            "val": job_id
            })

        if self.postgres.update('job', data, conditions):

            return 1

        return 0

    def send_email_vpn(self, job_id, token):
        """Send Email VPN"""

        sql_str = "SELECT * FROM job WHERE job_id={0} AND token='{1}'".format(job_id, token)
        job = self.postgres.query_fetch_one(sql_str)

        if job:

            sql_str = "SELECT email FROM account WHERE id={0}".format(job['account_id'])
            email = self.postgres.query_fetch_one(sql_str)

            if email:

                email = email['email']
                filename = job['directory'].split("/")[-1]
                url = 'http://' + job['vnp_server_ip'] + '/zip_vpn/' + filename

                vpn_dir = '/home/admin/all_vpn/' + filename

                urllib.request.urlretrieve(url, vpn_dir)

                # emailer = Email()
                # e_temp = Message()

                # msg = "Attached is your new VPN for new VPN configuration."
                # message = e_temp.message_temp(msg)
                # subject = "Web VPN"
                # if job['vpn_type'] in ['VCLIENT', 'VRH']:
                #     subject = "Vessel VPN"

                # instruction = './Instructions_OPENVPN.pdf'
                # emailer.send_email(email,
                #                    message,
                #                    subject,
                #                    [vpn_dir, instruction])

                # SEND AUTO INSTALL VPN
                self.send_auto_install(job, email)

                return 1

        return 0

    def add_vpn_ip(self, data, vpn_token, flag=False):
        """Add VPN IP"""

        api_endpoint = self.user_protocol + "://" + self.user_vpn + "/ovpn"

        if flag:

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/ovpn"

        headers = {'content-type': 'application/json', 'token': vpn_token}

        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)
        res = req.json()

        return res

    def insert_job(self, callback_url, data_url, vpn_token,
                   account_id, user_vpn, action, vpn_type):
        """Insert Job"""

        update_on = time.time()

        # INIT NEW JOB
        temp = {}
        temp['callback_url'] = callback_url
        temp['vnp_server_ip'] = user_vpn
        temp['data_url'] = data_url
        temp['token'] = vpn_token
        temp['status'] = 'pending'
        temp['account_id'] = account_id
        temp['vpn_type'] = vpn_type
        temp['action'] = action
        temp['update_on'] = update_on
        temp['created_on'] = update_on

        # INSERT NEW JOB
        job_id = self.postgres.insert('job',
                                      temp,
                                      'job_id'
                                     )

        return job_id

    def get_sa_role(self, account_id):
        """Return Account Role"""

        # OPEN CONNECTION
        self.postgres.connection()

        sql_str = "SELECT * FROM account_role where account_id='{0}' ".format(account_id)
        sql_str += "AND role_id in (SELECT role_id FROM role "
        sql_str += "WHERE role_name='super admin')"

        account = self.postgres.query_fetch_one(sql_str)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        return account

    def send_auto_install(self, job, email):
        """ Send email Auto install """

        account_id = job['account_id']
        sa_role = self.get_sa_role(account_id)

        # OPEN CONNECTION
        self.postgres.connection()

        sql_str = "SELECT * FROM account_vessel WHERE account_id={0} ".format(account_id)
        sql_str += "AND allow_access=true"

        acc_vessel = self.postgres.query_fetch_all(sql_str)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        filenames = []
        if acc_vessel or sa_role:

            # MUST HAVE TWO VPN
            sql_str = "SELECT * FROM job WHERE job_id in ("
            sql_str += "SELECT job_id FROM account_vpn WHERE "
            sql_str += "account_id={0} and status=true)".format(account_id)
            jobs = self.postgres.query_fetch_all(sql_str)
            if len(jobs) == 2:
                # SEND EMAIL
                for j in jobs:
                    filename = j['directory'].split("/")[-1]

                    filenames.append('/home/admin/all_vpn/' + filename)

                win_url, mac_url = self.installer_setup(account_id, filenames)

                self.send_installer_email(win_url, mac_url, email)
        else:

            # ONE VPN
            # SEND EMAIL
            filename = job['directory'].split("/")[-1]

            filenames.append('/home/admin/all_vpn/' + filename)

            win_url, mac_url = self.installer_setup(account_id, filenames)

            self.send_installer_email(win_url, mac_url, email)

        return 1

    def installer_setup(self, account_id, filenames):
        """ Installer Setup """

        installer_dir = '/home/admin/all_vpn/Installer/VPN_' + str(account_id) + '_Installer'

        # REMOVE DIRECTORY IF EXIST
        remove_command = 'rm -rf ' + installer_dir
        os.system(remove_command)

        # CREATE DIRECTORY
        create_dir = 'mkdir ' + installer_dir
        os.system(create_dir)

        # ------------------------- WINDOWS ------------------------- #
        # CREATE WINDOWS INSTALLER DIRECTORY
        iwindir = installer_dir + "/RHBox\ VPN\ Installer-WindowsOS"
        new_windir = 'mkdir ' + iwindir
        os.system(new_windir)

        # COPY WINDOWS INSTALL DIRECTORY
        original_iwinfiles = "/app/rhboxautoinstall/RHBox\ VPN\ Installer-WindowsOS/"
        iwinfiles = "cp -r " + original_iwinfiles + "* " + iwindir + "/"
        os.system(iwinfiles)

        # COPY WINDOWS VPN CREDENTIALS
        for fname in filenames:

            cp_command = 'cp ' + fname + ' ' + iwindir + '/' + 'VPN\ Credentials'
            os.system(cp_command)

        # ZIP WINDOWS INSTALLER
        oiwindir = installer_dir + "/RHBox VPN Installer-WindowsOS"
        shutil.make_archive(oiwindir, 'zip', oiwindir)

        # --------------------------- MAC --------------------------- #
        # CREATE MAC INSTALLER DIRECTORY
        imacdir = installer_dir + "/RHBox\ VPN\ Installer-MacOS"
        new_macdir = 'mkdir ' + imacdir
        os.system(new_macdir)

        # COPY MAC INSTALL DIRECTORY
        original_imacfiles = "/app/rhboxautoinstall/RHBox\ VPN\ Installer-MacOS/"
        imacfiles = "cp -r " + original_imacfiles + "* " + imacdir + "/"
        os.system(imacfiles)

        # COPY MAC VPN CREDENTIALS
        for fname in filenames:

            cp_command = 'cp ' + fname + ' ' + imacdir + '/' + 'VPNCredentials'
            os.system(cp_command)

        # ZIP MAC INSTALLER
        oimacdir = installer_dir + "/RHBox VPN Installer-MacOS"
        shutil.make_archive(oimacdir, 'zip', oimacdir)

        win_zip = oiwindir + '.zip'
        mac_zip = oimacdir + '.zip'

        return self.upload_vpn(win_zip, mac_zip, account_id)

    def upload_vpn(self, win_zip, mac_zip, account_id):
        """ VPN ACCESS """

        # AWS ACCESS
        aws_access_key_id = config_section_parser(self.config,
                                                  "AWS")['aws_access_key_id']
        aws_secret_access_key = config_section_parser(self.config,
                                                      "AWS")['aws_secret_access_key']
        region_name = config_section_parser(self.config, "AWS")['region_name']

        # CONNECT TO S3
        s3_resource = boto3.resource('s3',
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=region_name)

        s3_client = boto3.client('s3',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=region_name)

        win_url = self.s3_uploader('WINDOWS', win_zip, s3_resource,
                                   s3_client, account_id)
        mac_url = self.s3_uploader('MAC', mac_zip, s3_resource,
                                   s3_client, account_id)

        return [win_url, mac_url]

    def s3_uploader(self, ops, zipdir, s3_resource, s3_client, account_id):
        """ VPN uploader """

        # Bucket
        bucket = config_section_parser(self.config, "AWS")['bucket']

        # Filename
        filename = 'VPN/VPN_' + ops + '_Installer_' + str(account_id) + '.zip'

        # SAVE TO S3
        s3_resource.meta.client.upload_file(zipdir, bucket, filename)

        s3_params = {
            'Key': filename,
            'Bucket': bucket
        }

        # GET PRESIGNED URL
        pres_url = s3_client.generate_presigned_url('get_object',
                                                    Params=s3_params,
                                                    ExpiresIn=86400,
                                                    HttpMethod='GET')

        return pres_url

    def send_installer_email(self, win_url, mac_url, email):
        """ SEND INSTALLER EMAIL """

        emailer = Email()
        e_temp = VPNInstallTemp()

        # MESSAGE
        msg = "Your VPN credentials installer has created or modified. "
        msg += "Please select a URL that matches your Operating system."

        # NOTES
        note = "Note: URL to download the installer will expire in 24 hours. "
        note += "If you miss to download and the URL already expired, "
        note += "please contact the administrator."

        message = e_temp.vpn_mgs_temp(msg, note, win_url, mac_url)
        subject = "Radio Holland VPN Installer"

        emailer.send_email(email, message, subject)

        return 1


    def delete_user(self, job_id, token):
        """ DELETE USER """

        sql_str = "SELECT * FROM job WHERE job_id={0} AND token='{1}'".format(job_id, token)
        job = self.postgres.query_fetch_one(sql_str)

        if job:

            account_id = job['account_id']
            sa_role = self.get_sa_role(account_id)

            # OPEN CONNECTION
            self.postgres.connection()

            sql_str = "SELECT * FROM account_vessel WHERE account_id={0} ".format(account_id)
            sql_str += "AND allow_access=true"

            acc_vessel = self.postgres.query_fetch_all(sql_str)

            # CLOSE CONNECTION
            self.postgres.close_connection()

            conditions = []

            conditions.append({
                "col": "id",
                "con": "=",
                "val": account_id
                })


            sql_str = "SELECT is_active FROM account WHERE id={0}".format(account_id)
            active = self.postgres.query_fetch_one(sql_str)

            if acc_vessel or sa_role:

                self.postgres.connection()

                # MUST HAVE TWO VPN
                sql_str = "SELECT * FROM job WHERE job_id in ("
                sql_str += "SELECT job_id FROM account_vpn WHERE "
                sql_str += "account_id={0} and status=true)".format(account_id)

                jobs = self.postgres.query_fetch_all(sql_str)

                if len(jobs) == 2 and not active['is_active']:

                    # DELETE USER
                    self.postgres.delete('account', conditions)
            else:

                if not active['is_active']:

                    # DELETE USER
                    self.postgres.delete('account', conditions)

        return 1
