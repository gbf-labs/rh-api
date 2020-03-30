# pylint: disable=no-self-use
"""Reset Password"""
import time
import datetime

from configparser import ConfigParser
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

from library.emailer import Email
from templates.message import Message

class ResetPassword(Common):
    """Class for ResetPassword"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for ResetPassword class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.postgres = PostgreSQL()
        super(ResetPassword, self).__init__()

    def reset_password(self):
        """
        This API is for Reset Password
        ---
        tags:
          - User
        produces:
          - application/json
        parameters:
          - name: query
            in: body
            description: Reset Password
            required: true
            schema:
              id: Reset Password
              properties:
                reset_token:
                    type: string
                new_password:
                    type: string
                email:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: Reset Password
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)
        reset_token = query_json['reset_token']
        email = query_json['email']

        if not self.validate_reset_token(email, reset_token):

            data["alert"] = "Invalid email or Authentication key!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.set_new_password(query_json):

            data["alert"] = "Invalid email or Authentication key!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Password successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def set_new_password(self, query_json):
        """Set New Password"""

        # GET VALUES ROLE AND PERMISSION
        reset_token = query_json['reset_token']
        email = query_json['email']

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "email",
            "con": "=",
            "val": email
            })

        conditions.append({
            "col": "reset_token",
            "con": "=",
            "val": reset_token
            })

        # REMOVE KEYS
        query_json = self.remove_key(query_json, "email")
        query_json = self.remove_key(query_json, "reset_token")

        updates = {}
        updates['password'] = query_json['new_password']

        # UPDATE ROLE
        if self.postgres.update('account', updates, conditions):

            self.send_confirmation(email)
            # RETURN
            return 1

        # RETURN
        return 0


    def send_confirmation(self, email):
        """Send Confirmation"""

        emailer = Email()
        email_temp = Message()

        message = email_temp.message_temp("Your password is successfully changed.")
        subject = "Reset password confirmation"
        emailer.send_email(email, message, subject)

        return 1

    def validate_reset_token(self, email, reset_token):
        """Validate Reset Token"""

        sql_str = "SELECT reset_token_date FROM account WHERE"
        sql_str += " email='{0}' AND reset_token ='{1}'".format(email, reset_token)

        account = self.postgres.query_fetch_one(sql_str)

        if account:
            reset_token_date = account['reset_token_date']
            orig = datetime.datetime.fromtimestamp(reset_token_date)
            new = orig + datetime.timedelta(days=1)
            current_time = time.time()
            if new.timestamp() > current_time:
                return 1

        return 0
