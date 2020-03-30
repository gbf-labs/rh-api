# pylint: disable=too-many-public-methods, too-few-public-methods
"""Cron Update Vessel State"""
import time
from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.couch_queries import Queries
from library.couch_database import CouchDatabase

class UpdateVesselState(Common):
    """Class for UpdateVesselState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateVesselState class"""

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        super(UpdateVesselState, self).__init__()

    def update_vessel_state(self):
        """Update Vessel State"""

        vessels = self.couch_query.get_vessels()

        # JUST TO INDEX
        # self.couch_query.get_system1()

        vessel_ids = [x['id'] for x in vessels]

        # DON'T DELETE FOR SYSTEM INDEXING
        for vssl_id in vessel_ids:

            self.couch_query.get_system(vssl_id)

        # INIT SQL QUERY
        sql_str = "SELECT * FROM vessel"

        # FETCH ALL
        rows = self.postgres.query_fetch_all(sql_str)

        db_vessel_ids = [x['vessel_id'] for x in rows]

        vessel_ids = set(vessel_ids)
        db_vessel_ids = set(db_vessel_ids)

        vessel_ids.difference_update(db_vessel_ids)

        if vessel_ids:

            for vessel_id in vessel_ids:

                doc = self.couch_query.get_by_id(vessel_id)

                sql_str = "SELECT * FROM vessel WHERE "
                sql_str += "number='{0}'".format(doc['number'])

                vssl_nmbr = self.postgres.query_fetch_one(sql_str)

                if vssl_nmbr:

                    if vssl_nmbr['vessel_id'] and vssl_nmbr['number']:

                        # INIT CONDITION
                        conditions = []

                        # CONDITION FOR QUERY
                        conditions.append({
                            "col": "vessel_id",
                            "con": "=",
                            "val": vssl_nmbr['vessel_id']
                            })

                        data = {}
                        data['vessel_id'] = vessel_id

                        self.postgres.update('vessel', data, conditions)

                    else:

                        print("SAME VESSEL NUMBER: {0}!!!".format(vssl_nmbr['number']))

                else:

                    data = {}
                    data['number'] = doc['number']
                    data['vessel_name'] = self.get_vessel_name(vessel_id)
                    data['vessel_id'] = vessel_id
                    data['update_on'] = time.time()
                    data['created_on'] = time.time()

                    self.postgres.insert('vessel', data)

        sql_str = "SELECT * FROM vessel WHERE number IS NULL OR vessel_name IS NULL"
        null_vessels = self.postgres.query_fetch_all(sql_str)

        for vssl in null_vessels:

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "vessel_id",
                "con": "=",
                "val": vssl['vessel_id']
                })
            doc = self.couch_query.get_by_id(vssl['vessel_id'])

            if 'error' in doc.keys():
                number = vssl['vessel_id']

            else:
                number = doc['number']

            data = {}
            data['number'] = number
            data['vessel_name'] = self.get_vessel_name(vssl['vessel_id'])

            self.postgres.update('vessel', data, conditions)

        # RETURN
        return rows

    def get_vessel_name(self, vessel_id):
        """ Return Vessel Name """

        assert vessel_id, "Vessel ID is required."

        # GET VESSEL NAME
        values = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        if values:
            vessel_name = values['PARAMETERS']['INFO']['VESSELNAME']
        else:
            vessel_name = ""

        return vessel_name
