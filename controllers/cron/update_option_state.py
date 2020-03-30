# pylint: disable=too-few-public-methods
"""Update Option State"""
import time
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.couch_queries import Queries
from library.couch_database import CouchDatabase

class UpdateOptionState(Common):
    """Class for UpdateOptionState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateOptionState class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        super(UpdateOptionState, self).__init__()

    def update_option_state(self):
        """Update  Option State"""

        options = self.couch_query.get_options()
        option_ids = [x['_id'] for x in options]

        # INIT SQL QUERY
        sql_str = "SELECT * FROM option"

        # FETCH ALL
        rows = self.postgres.query_fetch_all(sql_str)

        db_option_ids = [x['option_id'] for x in rows]

        option_ids = set(option_ids)
        db_option_ids = set(db_option_ids)

        option_ids.difference_update(db_option_ids)

        if option_ids:

            opt_ids = list(option_ids)

            for option in options:

                if option['_id'] in opt_ids:

                    data = {}
                    data['option_id'] = option['_id']
                    data['option'] = option['option']
                    data['vessel_id'] = option['vessel_id']
                    data['update_on'] = time.time()
                    data['created_on'] = time.time()

                    self.postgres.insert('option', data)

        # RETURN
        return rows
