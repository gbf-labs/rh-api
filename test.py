#!/usr/bin/env python3
# pylint: disable=no-self-use, too-few-public-methods
"""Test"""
import json

import unittest

from configparser import ConfigParser
import requests

from library.config_parser import config_section_parser

CONFIG = ConfigParser()
CONFIG.read("config/config.cfg")

# HEADERS = {}
# HEADERS['Content-Type'] = 'application/json'
PORT = '5000'

class APIRequest():
    """Class for APIRequest"""

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor APIRequest class"""
    #     pass

    def api_post(self, url, data, head=None):
        """API Post"""
        api_ip = config_section_parser(CONFIG, "IPS")['my']
        api_protocol = config_section_parser(CONFIG, "IPS")['my_protocol']
        api_endpoint = api_protocol + "://" + api_ip + ":" + PORT + url

        headers = {}
        headers['content-type'] = 'application/json'

        if head:
            # headers = {**headers, **head}
            headers = {}

        req = requests.post(api_endpoint, data=json.dumps(data), headers=headers)

        return req.json()

class Test(unittest.TestCase):
    """Class for Test"""

    def setUp(self):
        """ SET UP """

        self.api_request = APIRequest()

        self.user_id = ""
        self.token = ""

        self.email = config_section_parser(CONFIG, "ADMIN")['username']
        self.password = config_section_parser(CONFIG, "ADMIN")['password']
        self.test_user_login()

    def test_user_login(self):
        """LOG IN"""
        data = {}
        data['email'] = self.email
        data['password'] = self.password

        response = self.api_request.api_post('/user/login', data)

        self.token = response['token']
        self.user_id = response['id']
        self.assertEqual(response['status'], True)

    def test_permission_create(self):
        """ CREATE PERMISSION """

        head = {}
        head['token'] = str(self.token)
        head['userid'] = str(self.user_id)

        url = '/permission/create'

        data = {}
        data['permission_details'] = 'DETAILS'
        data['permission_name'] = 'PERMISSION 103'

        response = self.api_request.api_post(url, data, head=head)

        self.assertEqual(response['status'], 'ok')

if __name__ == '__main__':
    unittest.main()
