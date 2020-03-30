# pylint: disable=no-self-use
"""Authentication Key"""
import time
from uuid import uuid4
from configparser import ConfigParser
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.emailer import Email
from templates.reset_token import ResetToken

class AuthenticationKey(Common):
    """Class for AuthenticationKey"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AunthenticationKey class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.postgres = PostgreSQL()
        super(AuthenticationKey, self).__init__()

    def authentication_key(self):
        """
        This API is for To send authentication key on user email
        ---
        tags:
          - User
        produces:
          - application/json
        parameters:
          - name: query
            in: body
            description: User authentication key
            required: true
            schema:
              id: User authentication key
              properties:
                email:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: User authentication key
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        if not self.insert_authentication_key(query_json):

            data["alert"] = "Email does not exist!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Authentication key has been send in your email!"
        data['status'] = "ok"
        return self.return_data(data)

    def insert_authentication_key(self, query_json):
        """Insert Authentication Key"""

        # GET VALUES ROLE AND PERMISSION
        email = query_json['email']
        reset_token = str(uuid4())[:8]
        updates = {}
        updates['reset_token_date'] = time.time()
        updates['reset_token'] = reset_token

        sql_str = "SELECT email FROM account WHERE"
        sql_str += " email='{0}'".format(email)

        if not self.postgres.query_fetch_one(sql_str):
            self.postgres.close_connection()
            return 0

        # INIT CONDITION
        conditions = []

        # CONDITION FOR QUERY
        conditions.append({
            "col": "email",
            "con": "=",
            "val": email
            })

        # UPDATE RESET TOKEN
        if self.postgres.update('account', updates, conditions):

            # SEND EMAIL FOR RESET PASSWORD
            self.send_authentication_key(email, reset_token)

            # RETURN
            return 1

        # RETURN
        return 0


    def send_authentication_key(self, email, reset_token):
        """Send Authentication Key"""

        email_temp = ResetToken()
        emailer = Email()

        message = email_temp.reset_token_temp(reset_token)
        subject = "Authentication key for password reset"
        emailer.send_email(email, message, subject)

        return 1
