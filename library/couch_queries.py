#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=too-many-arguments, too-many-branches
"""Couch Queries"""
import requests
from library.couch_database import CouchDatabase
from library.common import Common

class Queries(Common):
    """Class for Queries"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Vessels class"""
        self._couch_db = CouchDatabase()
        super(Queries, self).__init__()

    def get_device(self, vessel_id):
        """Return Device by Vessel ID"""
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/device/_view/get_device?'
        couch_query += 'startkey=["' + vessel_id + '"]&'
        couch_query += 'endkey=["' + vessel_id + '",{}]'
        couch_query += '&include_docs=true'

        res = requests.get(couch_query)
        json_data = res.json()
        rows = json_data['rows']

        data = []
        for row in rows:

            data.append(row['doc'])

        return data

    def get_by_id(self, couch_id):
        """Get By ID"""

        # GET MODULE
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/' + str(couch_id)

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()

        if json_data:

            return json_data

        return {}

    def get_vessels(self, vessel_number=None, limit=None, page=None):
        """Return Vessels"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/vessel/_view/get_vessels?'
        if vessel_number:
            couch_query += 'startkey="' + vessel_number + '"'
            couch_query += '&endkey="' + vessel_number + '"&'

        couch_query += 'include_docs=true'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()

        if limit and page:

            rows = json_data['rows']
            device_list = self.limits(rows, limit, page)

        else:

            device_list = json_data['rows']

        return device_list

    def get_system(self, vessel_id):
        """Return System"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/system/_view/get_system?'

        if vessel_id:

            couch_query += 'startkey=["' + vessel_id + '",9999999999]&'
            couch_query += 'endkey=["' + vessel_id + '",0]&'

        couch_query += 'include_docs=true&limit=1&descending=true'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()

        # RETURN
        return json_data

    # JUST FOR INDEXING THE DATE - WILL DELETE SOON
    def get_system1(self, limit=10, page=None):
        """Return System1"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/system/_view/get_system?limit=' + str(limit)

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()

        if limit and page:

            rows = json_data['rows']
            device_list = self.limits(rows, limit, page)

        else:

            device_list = json_data['rows']

        # RETURN
        return device_list

    def get_all_devices(self, vessel_id):
        """Return All Devices"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/device/_view/get_device?'
        couch_query += 'startkey=["' + vessel_id + '"]&'
        couch_query += 'endkey=["' + vessel_id + '",{}]&'
        couch_query += 'include_docs=true'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()
        device_list = json_data['rows']

        return device_list

    def get_complete_values(self, vessel_id, device, start=None, end=None, flag='one',
                            descending=True):
        """Return Complete Values"""
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/value/_view/get_value?'

        if start and end:
            couch_query += 'startkey=["' + vessel_id + '", "' + device + '",' + end + ']&'
            couch_query += 'endkey=["' + vessel_id + '", "' + device + '",' + start + ']'

            if flag == 'all':
                couch_query += '&include_docs=true&descending=true'
            else:
                if descending:

                    couch_query += '&include_docs=true&limit=1&descending=true'

                else:

                    couch_query += '&include_docs=true&limit=1'

        else:
            couch_query += 'startkey=["' + vessel_id + '", "' + device + '",9999999999]&'
            couch_query += 'endkey=["' + vessel_id + '", "' + device + '",0]'

            if flag == 'all':
                couch_query += '&include_docs=true&descending=true'
            else:
                couch_query += '&include_docs=true&limit=1&descending=true'

        res = requests.get(couch_query)
        json_data = res.json()

        data = []
        if 'rows' not in json_data.keys():
            print("Error: {0} Reason: {1}".format(json_data['error'], json_data['reason']))
        else:
            rows = json_data['rows']

            if rows:

                if flag == 'one':

                    if rows:
                        data = rows[0]['doc']['value']

                if flag == 'one_doc':

                    if rows:
                        data = rows[0]['doc']

                elif flag == 'all':

                    data = []
                    for row in rows:

                        data.append(row['doc'])

        return data

    def get_devices(self):
        """Return Devices from CouchDB"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/device/_view/get_device'
        couch_query += '?include_docs=true'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()
        rows = json_data['rows']

        data = []
        for row in rows:
            data.append(row['doc'])

        return data

    def get_modules(self):
        """Return Modules from CouchDB"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/module/_view/get_module'
        couch_query += '?include_docs=true'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()
        rows = json_data['rows']

        data = []
        for row in rows:
            data.append(row['doc'])

        return data

    def get_options(self):
        """Return Options from CouchDB"""
        # COUCH QUERY - GET VESSELS
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/option/_view/get_option'
        couch_query += '?include_docs=true'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()
        rows = json_data['rows']

        data = []
        for row in rows:
            data.append(row['doc'])

        return data

    def get_coredata(self, vessel_id, start=None, end=None, flag=None):
        """Return Corevalues Data"""
        couch_query = self._couch_db.couch_db_link()
        couch_query += '/_design/value/_view/get_value?'

        #if start and end:
        couch_query += 'startkey=["' + vessel_id + '", "COREVALUES",' + str(end) + ']&'
        couch_query += 'endkey=["' + vessel_id + '", "COREVALUES",' + str(start) + ']'
        couch_query += '&descending=true'

        if flag == "limit":
            couch_query += '&limit=1'

        # EXECUTE COUCH QUERY
        res = requests.get(couch_query)
        json_data = res.json()

        rows = json_data['rows']
        data = []

        for row in rows:
            data.append(row['key'][2])

        # RETURN
        return data

    def get_last_ini(self, vessel_id):
        """ GET LAST INI FILE DATA """

        couch_query = self._couch_db.couch_db_link()
        couch_query += "/_design/ini/_view/get_ini?"
        couch_query += "startkey=[\"{0}\", 9999999999]".format(vessel_id)
        couch_query += "&endkey=[\"{0}\", 0]".format(vessel_id)
        couch_query += "&include_docs=true&limit=1&descending=true"
        res = requests.get(couch_query)
        json_data = res.json()

        if 'rows' in json_data.keys():

            return json_data['rows']

        return 0
