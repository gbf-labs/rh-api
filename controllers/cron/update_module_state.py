# pylint: disable=too-few-public-methods
"""Update Module State"""
import time
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.couch_queries import Queries
from library.couch_database import CouchDatabase

class UpdateModuleState(Common):
    """Class for UpdateModuleState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateModuleState class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        super(UpdateModuleState, self).__init__()

    def update_module_state(self):
        """Update Module State"""

        modules = self.couch_query.get_modules()
        module_ids = [x['_id'] for x in modules]

        # INIT SQL QUERY
        sql_str = "SELECT * FROM module"

        # FETCH ALL
        rows = self.postgres.query_fetch_all(sql_str)

        db_module_ids = [x['module_id'] for x in rows]

        module_ids = set(module_ids)
        db_module_ids = set(db_module_ids)

        module_ids.difference_update(db_module_ids)

        if module_ids:

            mdl_ids = list(module_ids)

            for module in modules:

                if module['_id'] in mdl_ids:

                    data = {}
                    data['module_id'] = module['_id']
                    data['module'] = module['module']
                    data['vessel_id'] = module['vessel_id']
                    data['update_on'] = time.time()
                    data['created_on'] = time.time()

                    self.postgres.insert('module', data)

        # RETURN
        return rows
