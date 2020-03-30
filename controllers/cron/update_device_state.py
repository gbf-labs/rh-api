# pylint: disable=too-few-public-methods
"""Update Device State"""
import time
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.couch_queries import Queries
from library.couch_database import CouchDatabase

class UpdateDeviceState(Common):
    """Class for UpdateDeviceState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateDeviceState class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        super(UpdateDeviceState, self).__init__()

    def update_device_state(self):
        """Update Device State"""

        devices = self.couch_query.get_devices()
        device_ids = [x['_id'] for x in devices]

        # INIT SQL QUERY
        sql_str = "SELECT * FROM device"

        # FETCH ALL
        rows = self.postgres.query_fetch_all(sql_str)

        db_device_ids = [x['device_id'] for x in rows]

        device_ids = set(device_ids)
        db_device_ids = set(db_device_ids)

        device_ids.difference_update(db_device_ids)

        if device_ids:

            d_ids = list(device_ids)

            for device in devices:

                if device['_id'] in d_ids:

                    parameters = self.couch_query.get_complete_values(
                        device['vessel_id'],
                        "PARAMETERS"
                    )

                    if device['device'] in ['COREVALUES', 'FAILOVER', 'PARAMETERS', 'NTWCONF']:
                        device_type = device['device']
                    else:
                        device_type = parameters['PARAMETERS'][device['device']]['TYPE']

                    data = {}
                    data['device_id'] = device['_id']
                    data['device'] = device['device']
                    data['device_type'] = device_type
                    data['vessel_id'] = device['vessel_id']
                    data['update_on'] = time.time()
                    data['created_on'] = time.time()

                    self.postgres.insert('device', data)

        # RETURN
        return rows
