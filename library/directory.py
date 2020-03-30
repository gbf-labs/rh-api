# pylint: disable=too-few-public-methods
"""Directory"""
from configparser import ConfigParser
from library.config_parser import config_section_parser

class Directory():
    """Class for Directory"""

    def __init__(self):
        """The Constructor for Directory class"""
        # INIT CONFIG
        self.config = ConfigParser()
        # CONFIG FILE
        self.config.read("config/config.cfg")

        # WEB DIRECTORY
        self.web_directory = config_section_parser(self.config, "PATH")['web']
