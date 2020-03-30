# pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-locals, too-many-statements
"""Update INI Files"""
import time
import json
from configparser import ConfigParser
import requests
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.couch_queries import Queries
from library.couch_database import CouchDatabase
from library.config_parser import config_section_parser

class UpdateINIFiles(Common):
    """Class for UpdateINIFiles"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateINIFiles class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")


        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        super(UpdateINIFiles, self).__init__()

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']

        self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']
        self.vessel_protocol = config_section_parser(self.config, "IPS")['vessel_protocol']

        self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'

    def update_ini_files(self):
        """Update  INI Files"""

        # INIT SQL QUERY
        sql_str = "SELECT * FROM vessel"

        # FETCH ALL
        rows = self.postgres.query_fetch_all(sql_str)

        for row in rows:
            vessel_id = row['vessel_id']
            inifiles = self.couch_query.get_last_ini(vessel_id)

            if inifiles:

                vdatas = inifiles[0]["doc"]["data"]
                vtimestamp = inifiles[0]["doc"]["timestamp"]
                ini_dir = vdatas[list(vdatas.keys())[0]]['dir']

                sql_str = "SELECT * FROM ini_files WHERE "
                sql_str += "vessel_id='{0}' AND dir='{1}'".format(vessel_id, ini_dir)

                sdata = self.postgres.query_fetch_one(sql_str)
                if not sdata:

                    for vdata in vdatas.keys():

                        newdt = {}
                        newdt['vessel_id'] = vessel_id
                        newdt['dir'] = vdatas[vdata]['dir']
                        newdt['content'] = json.dumps(vdatas[vdata]['content'])
                        newdt['lastupdate'] = vtimestamp
                        newdt['vessel_lastupdate'] = vtimestamp
                        newdt['created_on'] = time.time()
                        newdt['update_on'] = time.time()

                        self.postgres.insert('ini_files', newdt, 'ini_files_id')

                else:

                    if int(vtimestamp) > int(sdata['lastupdate']):

                        for vdata in vdatas.keys():

                            ini_dir = vdatas[vdata]['dir']

                            conditions = []

                            conditions.append({
                                "col": "vessel_id",
                                "con": "=",
                                "val": vessel_id
                                })

                            conditions.append({
                                "col": "dir",
                                "con": "=",
                                "val": ini_dir
                                })

                            updata = {}
                            updata['content'] = json.dumps(vdatas[vdata]['content'])
                            updata['lastupdate'] = vtimestamp
                            updata['vessel_lastupdate'] = vtimestamp

                            self.postgres.update('ini_files', updata, conditions)

                    if int(vtimestamp) < int(sdata['lastupdate']):

                        # UPDATE VESSEL INIFILES
                        self.send_command(vessel_id)

            vsystem = self.couch_query.get_system(vessel_id)
            if vsystem["rows"]:

                vsystem = vsystem["rows"][0]["doc"]["data"]
                repos = set(["ui_version", "api_version", "backend_version"])
                sys_keys = set(vsystem.keys())

                if repos.issubset(sys_keys):

                    ui_version = vsystem["ui_version"]
                    api_version = vsystem["api_version"]
                    backend_version = vsystem["backend_version"]

                    ui_version = ui_version.split("\n")[0]
                    api_version = api_version.split("\n")[0]
                    backend_version = backend_version.split("\n")[0]

                    sql_str = "SELECT * FROM vessel_version INNER JOIN version ON"
                    sql_str += " vessel_version.version_id=version.version_id WHERE"
                    sql_str += " (vessel_version.vessel_id='{0}')".format(vessel_id)
                    sql_str += " and (version.web!='{0}'".format(ui_version)
                    sql_str += " or version.api!='{0}'".format(api_version)
                    sql_str += " or version.backend!='{0}')".format(backend_version)
                    vversion = self.postgres.query_fetch_one(sql_str)

                    if vversion:

                        # UPDATE VERSION
                        self.update_version(vessel_id, vversion)

        return 1

    def update_version(self, vessel_id, datas):
        """UPDATE VESSEL VERSION"""

        ntwconf_datas = self.couch_query.get_complete_values(
            vessel_id,
            "NTWCONF",
            flag='one_doc'
        )

        ntwconf = ntwconf_datas['value']
        current_time = time.time()
        ntwconf_timestamp = ntwconf_datas['timestamp']

        if self.check_time_lapse(current_time, ntwconf_timestamp) == 'green':

            host = ntwconf['NTWCONF']['tun1']['IP']
            data = {}
            data['host'] = host
            data['port'] = 8080
            data['ini_data'] = datas

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/update/ini/files"

            headers = {'content-type': 'application/json', 'token': self.vpn_token}
            req = requests.put(api_endpoint, data=json.dumps(data), headers=headers)
            res = req.json()

            return res

        return 0

    def send_command(self, vessel_id):
        """Send Command"""

        ini_data = self.get_ini_files(vessel_id)

        ntwconf_datas = self.couch_query.get_complete_values(
            vessel_id,
            "NTWCONF",
            flag='one_doc'
        )

        ntwconf = ntwconf_datas['value']
        current_time = time.time()
        ntwconf_timestamp = ntwconf_datas['timestamp']

        if self.check_time_lapse(current_time, ntwconf_timestamp) == 'green':

            host = ntwconf['NTWCONF']['tun1']['IP']
            data = {}
            data['host'] = host
            data['port'] = 8080
            data['ini_data'] = ini_data['datas']

            api_endpoint = self.vessel_protocol + "://" + self.vessel_vpn + "/update/ini/files"

            headers = {'content-type': 'application/json', 'token': self.vpn_token}
            req = requests.put(api_endpoint, data=json.dumps(data), headers=headers)
            res = req.json()

            return res

        return 0

    def get_ini_files(self, vessel_id):
        """Return INI Files"""

        # GET SUPER ADMIN ID
        sql_str = "SELECT * FROM ini_files WHERE vessel_id ='{0}'".format(vessel_id)
        ini_files = self.postgres.query_fetch_all(sql_str)

        datas = {}

        for ini_file in ini_files:

            datas[ini_file['dir']] = "\n".join(ini_file['content'])

        final_data = {}
        final_data['filenames'] = [x['dir'] for x in ini_files]
        final_data['datas'] = datas

        return final_data
