#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=too-few-public-methods, unreachable
"""Announcement"""
import subprocess
import shlex
import time
from flask import request
from library.common import Common
from library.directory import Directory

class Announcement(Common):
    """Class for Announcement"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Announcement class"""
        self.directory = Directory()
        super(Announcement, self).__init__()

    # GET ANNOUNCEMENT FUCNTION
    def get_announcement(self):
        """
        This API is for Getting Announcement Information
        ---
        tags:
          - Announcement
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
        responses:
          500:
            description: Error
          200:
            description: Announcement Information
        """

        # INIT DATA
        data = {}

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
        # SET DEFAULT RETURN
        data['status'] = 'ok'
        data['rows'] = []

        return self.return_data(data)

        # SET GIT COMMAND
        web_dir = self.directory.web_directory
        git_cmd = 'git --git-dir=' + web_dir + '.git/ log'
        git_cmd += ' --grep=[[Nn][Ee][Ww][Ss]] --max-count=15'
        git_cmd += ' --format=format:"commit;%H;%ct;%s"'

        # INIT VARIABLE
        kwargs = {}
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

        # RUN GIT COMMAND
        proc = subprocess.Popen(shlex.split(git_cmd), **kwargs)
        # LOOP RETURN FROM PROC
        for line in iter(proc.stdout.readline, ''):

            # SET DATA FOR RETURN
            row = {}
            array_line = line.rstrip().split(';')
            hash_data = array_line[1]
            epoch = float(array_line[2])
            subject = array_line[3].replace('[News]', '')

            # RETURN DATA
            row['hash'] = hash_data
            row['subject'] = subject
            row['time'] = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(epoch))
            data['rows'].append(row)

        # RETURN
        return self.return_data(data)
