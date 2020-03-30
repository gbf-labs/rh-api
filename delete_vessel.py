#!/usr/bin/env python3
# coding: utf-8
# pylint: disable=bare-except
"""Delete Vessel"""
import sys
import time
import json
import requests

from library.couch_database import CouchDatabase
from library.postgresql_queries import PostgreSQL

COUCHDB = CouchDatabase()
POSTGRES = PostgreSQL()

# couch_query = COUCHDB.couch_db_link()

def single_delete(doc_id, rev):
    """Single Delete"""
    url = COUCHDB.couch_db_link()
    url += '/' + doc_id + '?' + 'rev=' + rev
    headers = {"Content-Type" : "application/json"}
    response = requests.delete(url, headers=headers)
    response = response.json()

    return response

def bulk_delete(query):
    """Bulk Delete"""
    count = 1

    while True:

        req = requests.get(query)

        rows = json.loads(req.text)['rows']

        if not rows:

            break

        todelete = []

        for doc in rows:

            count += 1

            todelete.append({"_deleted": True,
                             "_id": doc["doc"]["_id"],
                             "_rev": doc["doc"]["_rev"]
                            })

        url = COUCHDB.couch_db_link()
        url += "/_bulk_docs"

        requests.post(url, json={"docs": todelete})

def delete_query(vessel_id, dsgn):
    """Delete Query"""
    view = "get_" + dsgn

    query = COUCHDB.couch_db_link()
    query += "/_design/{0}/_view/{1}?".format(dsgn, view)
    query += "startkey=[\"{0}\"]&endkey=[\"{0}\",".format(vessel_id)
    query += "{}]&include_docs=true&limit=1000"

    return query

def delete_vssl(vessel_id):
    """Delete Vessel"""
    conditions = []

    conditions.append({
        "col": "vessel_id",
        "con": "=",
        "val": vessel_id
        })

    if POSTGRES.delete('vessel', conditions):
        # print("Vessel {0} deleted!".format(vessel_id))
        return 1

    # print("Vessel {0} not deleted!".format(vessel_id))
    return 0


def delete_alarm_vessel(vessel_id):
    """Delete Alarm Vessel"""
    # OPEN CONNECTION
    POSTGRES.connection()

    # DATA
    sql_str = "SELECT * FROM alarm_value"
    sql_str += " WHERE vessel LIKE '%{0}%'".format(vessel_id)
    datas = POSTGRES.query_fetch_all(sql_str)

    if datas:

        for data in datas:

            vessel = []

            for vssl in data['vessel'].split(","):
                vessel.append(vssl)

            ves = vessel.index(vessel_id)

            condition = []

            condition.append({
                "col": "alarm_value_id",
                "con": "=",
                "val": data['alarm_value_id']
            })

            if len(vessel) > 1:

               #DELETE VESSEL ON VESSEL LIST
                del vessel[ves]

                alarm_data = {}
                alarm_data['vessel'] = ",".join(vessel)
                alarm_data['update_on'] = time.time()

                # UPDATE ALARM VALUE
                if POSTGRES.update('alarm_value', alarm_data, condition):
                    pass
                    # print("Alarm Value has been successfully updated.")

                else:
                    # print("Failed to update alarm value")
                    pass

            else:

                #IF ONLY ONE VESSEL DELETE ALARM VALUE ROW
                if POSTGRES.delete('alarm_value', condition):
                    # print("Alarm Value has been successfully deleted!")
                    pass

                else:
                    # print("Failed to delete alarm value.")
                    pass

    # CLOSE CONNECTION
    POSTGRES.close_connection()

    return 1

DESIGNS = ["device", "module", "option", "system", "value"]

try:

    VESSEL_ID = sys.argv[1]
    VESSEL_REV = sys.argv[2]


except:

    VESSEL_ID = "a62784ebf1791db5d8ba89e7f2000a95"

    VESSEL_REV = "1-c347a5c4bc4a87046cb15864267711a2"

    # print("No parameters!")
    # print("ex: python3 delete_vessel.py {0} {1}".format(VESSEL_ID, VESSEL_REV))

    sys.exit(0)

RES = single_delete(VESSEL_ID, VESSEL_REV)

# print ("response: ", RES)

delete_vssl(VESSEL_ID)

delete_alarm_vessel(VESSEL_ID)

for design in DESIGNS:

    q = delete_query(VESSEL_ID, design)
    bulk_delete(q)

    # print(" All {0} are deleted!".format(design))

# BEFORE RUN THIS
# sudo service uwsgi stop && sudo service nginx stop
