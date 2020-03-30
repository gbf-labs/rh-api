"""Indexing"""
import logging
import time
from multiprocessing import Process, Value
from flask import Flask


import requests
from library.couch_database import CouchDatabase

# logging.basicConfig(filename='/home/admin/log_file_name.log', level=logging.INFO)

APP = Flask(__name__)

class Indexing():
    """Indexing"""

    # INITIALIZE
    def __init__(self):
        """The constructor for Indexing class"""
        self._couch_db = CouchDatabase()

    def index_device(self):
        """Index Device"""
        # GET MODULE
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/device/_view/get_device?'
        couch_query += 'limit=1'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)

        json_data = res.json()
        if json_data['rows']:
            value = json_data['rows']
            return value
        return 0

    def index_module(self):
        """Index Module"""
        # GET MODULE
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/module/_view/get_module?'
        couch_query += 'limit=1'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)

        json_data = res.json()
        if json_data['rows']:
            value = json_data['rows']
            return value
        return 0

    def index_option(self):
        """Index Option"""
        # GET MODULE
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/option/_view/get_option?'
        couch_query += 'limit=1'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)

        json_data = res.json()
        if json_data['rows']:
            value = json_data['rows']
            return value
        return 0

    def index_value(self):
        """Index Value"""
        # GET MODULE
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/value/_view/get_value?'
        couch_query += 'limit=1'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)

        json_data = res.json()
        if json_data['rows']:
            value = json_data['rows']
            return value
        return 0

    def index_vessel(self):
        """Vessel Index"""
        # GET MODULE
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/vessel/_view/get_vessels?'
        couch_query += 'limit=1'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)

        json_data = res.json()
        if json_data['rows']:
            value = json_data['rows']
            return value
        return 0

#def record_loop(loop_on):
def record_loop():
    """Record Loop"""

    while True:

        log = logging.getLogger(__name__)
        log.info('hello world')

        logging.basicConfig(filename='/home/admin/log_file_name.log', level=logging.INFO)
        index = Indexing()
        if index.index_device():
            logging.info("Device: OK!")
        else: logging.info("Device: Error")
        if index.index_module():
            logging.info("Module: OK!")
        else: logging.info("Module: Error")
        if index.index_option():
            logging.info("Option: OK!")
        else: logging.info("Option: Error")
        if index.index_value():
            logging.info("Value: OK!")
        else: logging.info("Value: Error")
        if index.index_vessel():
            logging.info("Vessel: OK!")
        else: logging.info("Vessel: Error")

        time.sleep(120)

if __name__ == "__main__":
    logging.info("Device: ----------------------------!")
    logging.info("Device: ----------------------------!")
    logging.info("Device: ----------------------------!")
    RECORDING_ON = Value('b', True)
    PROC = Process(target=record_loop, args=(RECORDING_ON,))
    PROC.start()
    APP.run(debug=True, use_reloader=False)
    PROC.join()
