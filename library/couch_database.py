# pylint: disable=no-self-use, too-many-instance-attributes, attribute-defined-outside-init
"""Couch Database"""
from configparser import ConfigParser
import requests
import couchdb
from library.config_parser import config_section_parser

class CouchDatabase():
    """Class for CouchDatabase"""

    def __init__(self):
        """The Constructor for CouchDatabase class"""
        # INIT CONFIG
        self.config = ConfigParser()
        # CONFIG FILE
        self.config.read("config/config.cfg")

        # COUCH DATABASE NAME
        self.couchdb_name = config_section_parser(self.config, "COUCHDB")['db_name']

        # COUCH CREDENTIALS
        self.couch_protocol = config_section_parser(self.config, "COUCHDB")['protocol']
        self.couch_user = config_section_parser(self.config, "COUCHDB")['user']
        self.couch_password = config_section_parser(self.config, "COUCHDB")['password']
        self.couch_host = config_section_parser(self.config, "COUCHDB")['host']
        self.couch_port = config_section_parser(self.config, "COUCHDB")['port']

    def connect_to_couch_db(self):
        """Connect to Couch Database"""
        # CONNECT TO COUCH DATABASE
        self.couch = couchdb.Server("%s://%s:%s@%s:%s/"%(self.couch_protocol,
                                                         self.couch_user,
                                                         self.couch_password,
                                                         self.couch_host,
                                                         self.couch_port
                                                        ))

    def couch_db_link(self):
        """Return Couch DB Link"""
        couch_query = self.couch_protocol + '://'+ self.couch_user
        couch_query += ':' + self.couch_password + '@' + self.couch_host
        couch_query += ':' + self.couch_port
        couch_query += '/' + self.couchdb_name

        return couch_query

    def couch_query_one(self, couch_query):
        """Couch Query One"""
        res = requests.get(couch_query)
        json_data = res.json()

        if json_data['rows']:

            return json_data['rows'][0]

        return {}

    def couch_query_all(self, couch_query):
        """Couch Query All"""
        res = requests.get(couch_query)
        json_data = res.json()

        if json_data['rows']:

            return json_data['rows']

        return []

    def couch_db_url(self, design=None):
        """Couch Database URL"""
        couch_query = self.couch_protocol + '://'+ self.couch_user
        couch_query += ':' + self.couch_password + '@' + self.couch_host
        couch_query += ':' + self.couch_port
        couch_query += '/' + self.couchdb_name + '/'

        if design:
            couch_query += design

        return couch_query
