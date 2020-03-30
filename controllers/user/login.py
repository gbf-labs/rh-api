# pylint: disable=no-self-use
"""Login"""
# import logging
import time
from flask import request

from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.sha_security import ShaSecurity

class Login(Common, ShaSecurity):
    """Class for Login"""

    def __init__(self):
        """The Constructor for Login class"""
        self.postgres = PostgreSQL()
        super(Login, self).__init__()

    # LOGIN FUNCTION
    def login(self):
        """
        This API is use for login
        ---
        tags:
          - User
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: query
            in: body
            description: Login
            required: true
            schema:
              id: Login
              properties:
                email:
                    type: string
                password:
                    type: string
        responses:
          500:
            description: Error
          200:
            description: User Information
        """

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # INSTANTIATE VARIABLES
        json_return = {}
        # account_table = "account"

        # GET REQUEST PARAMS
        email = query_json["email"]
        password = query_json["password"]

        # CHECK IF USER EXIST
        user_data = self.get_user_data(email)

        # CHECK USERNAME
        if user_data:
            if "no_username" in user_data['username']:
                user_data['username'] = ""

        if not user_data:

            json_return["alert"] = "Invalid Username or Password!"
            json_return['status'] = 'Failed'
            # logging.warning("Email does not exists, email: %s " % email)

            # RETURN
            return self.return_data(json_return)

        # CHECK IF USER STATUS IS ACTIVE
        if not self.check_user_status(user_data):

            json_return["alert"] = "User is deactivated!"
            json_return['status'] = 'Failed'
            # logging.warning("User is deactivated, email: %s " % email)

            # RETURN
            return self.return_data(json_return)

        # CHECK PASSWORD
        if not self.check_password(password, user_data):

            json_return["alert"] = "Invalid Username or Password!"
            json_return['status'] = 'Failed'
            # logging.warning("Invalid Username or Password")

            # CLOSE DB CONNECTION
            self.postgres.close_connection()

            # RETURN
            return self.return_data(json_return)

        # UPDATE TOKEN
        user_data = self.update_token(user_data)

        user_data = self.remove_key(user_data, "password")
        user_data = self.remove_key(user_data, "created_on")
        user_data = self.remove_key(user_data, "last_login")

        # CLOSE DB CONNECTION
        self.postgres.close_connection()

        # RETURN
        return self.return_data(user_data)

    # GET USER INFO
    def get_user_data(self, email):
        """Return User Information"""

        # CREATE SQL QUERY
        # sql_str = "SELECT * FROM " + table + " WHERE email=\'"+email+"\'"
        sql_str = """
        SELECT a.id, a.username, a.email, a.status, a.password, (
        SELECT array_to_json(array_agg(role_perm)) FROM (
        SELECT r.role_id, r.role_name, r.role_details, (
        SELECT array_to_json(array_agg(p)) FROM permission p 
        INNER JOIN role_permission rp ON 
        rp.permission_id = p.permission_id 
        WHERE rp.role_id = r.role_id) AS permissions 
        FROM role r INNER JOIN account_role ar 
        ON ar.role_id = r.role_id 
        WHERE ar.account_id = a.id) AS role_perm) AS roles, (
        SELECT array_to_json(array_agg(c)) FROM company c 
        INNER JOIN account_company ac 
        ON ac.company_id = c.company_id 
        WHERE ac.account_id = a.id) AS companies FROM account a
        """
        sql_str += " WHERE email='{0}' OR username='{0}'".format(email)

        # GET USER INFO
        user_data = self.postgres.query_fetch_one(sql_str)

        # CHECK IF USER EXIST
        if not user_data:

            # RETURN
            return 0

        # RETURN
        return user_data

    # CHECK USER STATUS
    def check_user_status(self, user_data):
        """Check User Status"""

        # CHECK IF STATUS IS TRUE OR 1
        if user_data["status"]:

            # RETURN
            return 1

        # RETURN
        return 0

    # CHECK PASSWORD
    def check_password(self, password, user_data):
        """Check User Password"""

        # CHECK PASSWORD
        if password == user_data["password"]:

            # RETURN
            return 1

        # RETURN
        return 0

    def update_token(self, user_data):
        """Update Token"""

        new_token = self.generate_token()

        data = {}
        data['token'] = new_token
        data['update_on'] = time.time()
        data['last_login'] = time.time()

        condition = []
        temp_con = {}

        temp_con['col'] = 'id'
        temp_con['val'] = user_data["id"]
        temp_con['con'] = "="
        condition.append(temp_con)

        if self.postgres.update('account', data, condition):

            user_data["token"] = new_token

        return user_data
