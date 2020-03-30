# pylint: disable=no-self-use, too-many-locals, too-many-statements, too-many-branches, too-many-nested-blocks, unidiomatic-typecheck,consider-iterating-dictionary
"""Graph"""
import time
import datetime
import re

from flask import request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.postgresql_queries import PostgreSQL

class Graph(Common):
    """Class for Graph"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Graph class"""
        self.postgres = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        super(Graph, self).__init__()

    def graph(self):

        """
        This API is for Getting Graph
        ---
        tags:
          - Graph
        produces:
          - application/json
        parameters:
          - name: token
            in: header
            description: Token
            required: true
            type: string
          - name: userid
            in: header
            description: User ID
            required: true
            type: string
          - name: vessel_id
            in: query
            description: Vessel ID
            required: true
            type: string
          - name: device_id
            in: query
            description: Device ID
            required: true
            type: string
          - name: hours
            in: query
            description: Hours
            required: false
            type: integer
          - name: keys
            in: query
            description: Keys
            required: true
            type: string
          - name: combine
            in: query
            description: combine
            required: true
            type: boolean
          - name: start_time
            in: query
            description: Epoch start
            required: false
            type: string
          - name: end_time
            in: query
            description: Epoch end
            required: false
            type: string

        responses:
          500:
            description: Error
          200:
            description: Vessel Device Info
        """

        data = {}

        # VESSEL ID
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        keys = request.args.get('keys')
        combine = request.args.get('combine')
        hours = request.args.get('hours')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not vessel_id:

            data["alert"] = "Please complete parameters!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if device_id in ['COREVALUES', 'FAILOVER', 'NTWPERF1']:

            all_devices = self.couch_query.get_all_devices(vessel_id)
            for dev in all_devices:

                if dev['doc']['device'] == device_id:
                    device = dev['doc']
                    break
        else:

            device = self.couch_query.get_by_id(device_id)


        # hours_ago_epoch_ts = int(hours_ago.timestamp())
        # current_time = int(ctime.timestamp())
        if not start_time and not end_time:
            ctime = datetime.datetime.now()
            hours_ago = ctime - datetime.timedelta(hours=int(hours))
            start_time = int(hours_ago.timestamp())
            end_time = int(ctime.timestamp())

        values = self.couch_query.get_complete_values(
            vessel_id,
            device['device'],
            str(start_time),
            str(end_time),
            'all'
        )

        # temp_available_options = []
        # str_available_options = []
        # available_options = []
        opt = []
        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        if device['device'] == "COREVALUES":

            device_type = "COREVALUES"

        elif device['device'] == "NTWPERF1":

            device_type = "NTWPERF1"

        elif device['device'] == 'FAILOVER':

            device_type = 'FAILOVER'

        else:

            device_type = parameters['PARAMETERS'][device['device']]['TYPE']

        if combine.upper() == 'TRUE':

            final_data = []

            for value in values:

                timestamp = float(value['timestamp'])

                dev_value = value['value'][device['device']]

                # if  re.findall(r'VDR\d', device['device']):
                #     print("ALP ", dev_value)
                #     pass

                if  re.findall(r'NMEA\d', device['device']):

                    nmea_data = self.get_nmea_data(dev_value)
                    opt = list(set(self.get_graph_options(nmea_data)))
                    options = self.get_device_options(nmea_data)

                    if keys:
                        final_data.append(self.set_values(options, keys, timestamp))

                else:
                    opt = list(set(self.get_graph_options(dev_value)))
                    options = self.get_device_options(dev_value)

                    if keys:
                        final_data.append(self.set_values(options, keys, timestamp))

            final_data = sorted(final_data, key=lambda i: i['name'])

            for fdata in final_data:

                fdata['name'] = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(
                    float(fdata['name'])))

            data['data'] = final_data
            data['statistics'] = self.get_stat(final_data, flag=True)
        else:

            # FINAL DATA
            fnl_data = {}

            # SET DYNAMIC VARIABLE
            if keys:

                for key in keys.split(","):

                    fnl_data[key] = []

                for value in values:

                    timestamp = float(value['timestamp'])
                    dev_value = value['value'][device['device']]

                    # if  re.findall(r'VDR\d', device['device']):
                    #     print("ALP ", dev_value)
                    #     pass

                    if  re.findall(r'NMEA\d', device['device']):
                        nmea_data = self.get_nmea_data(dev_value)
                        opt = list(set(self.get_graph_options(nmea_data)))
                        options = self.get_device_options(nmea_data)

                        for key in keys.split(","):
                            fnl_data[key].append(self.set_values(options, key, timestamp))

                    else:
                        opt = list(set(self.get_graph_options(dev_value)))
                        options = self.get_device_options(dev_value)
                        for key in keys.split(","):
                            fnl_data[key].append(self.set_values(options, key, timestamp))

                for key in keys.split(","):

                    fnl_data[key] = sorted(fnl_data[key], key=lambda i: i['name'])

                    for fdata in fnl_data[key]:

                        fdata['name'] = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(float(
                            fdata['name'])))

            data['data'] = fnl_data
            data['statistics'] = self.get_stat(fnl_data, flag=False)

        # SET SQL QUERY
        sql_str = "SELECT * FROM selected_label"
        sql_str += " WHERE device_type='{0}' and select_type != 'combine'".format(device_type)
        default_selected = self.postgres.query_fetch_all(sql_str)

        # SET SQL QUERY
        sql_str = "SELECT * FROM selected_label"
        sql_str += " WHERE device_type='{0}' and select_type = 'combine'".format(device_type)
        default_selected_combine = self.postgres.query_fetch_all(sql_str)

        data['default_selected_combine'] = self.set_select_values(default_selected_combine)
        data['default_selected'] = self.set_select_values(default_selected)
        data['available_options'] = self.format_filter(opt)
        data['status'] = 'ok'

        return self.return_data(data)

    def set_values(self, options, keys, timestamp):
        """Set Values"""

        temp_data = {}

        for key in keys.split(","):

            if key in options.keys():

                if key in ['AntennaStatus', 'TxMode']:

                    if options[key].upper() in ['TRACKING', 'ON']:
                        temp_data[key] = 1
                    else:
                        temp_data[key] = 0

                elif key == 'error':

                    if options[key] is True:
                        temp_data[key] = 1
                    else:
                        temp_data[key] = 0

                else:
                    temp_data[key] = options[key]
            else:
                temp_data[key] = None

        temp_data['name'] = timestamp

        return temp_data

    def get_available_options(self, options, temp_available_options, str_available_options):
        """Return Available Options"""
        # print("Options --------------------------- >>")
        # print(options)
        # print("Options --------------------------- >>")
        available_options = []

        for opt in options.keys():

            if opt not in temp_available_options and opt not in str_available_options:

                if not options[opt]:
                    continue

                if type(options[opt]) == 'str':
                    if options[opt].isdigit():

                        options[opt] = float(options[opt])

                if self.isfloat(options[opt]) or self.isint(options[opt]) or opt in [
                        'AntennaStatus', 'TxMode']:

                    temp_available_options.append(opt)
                    temp = {}
                    temp['value'] = opt
                    temp['label'] = opt
                    available_options.append(temp)

                # else:
                #     str_available_options.append(op)

        return available_options

    def get_nmea_data(self, datas):
        """ Return NMEA Data """
        temp_data = {}
        # keys = [data for data in datas.keys()] # No need

        for key in list(datas.keys()):
            temp_data.update(datas[key])

        return temp_data

    def get_graph_options(self, datas):
        """Return Options for Graph"""
        options = []

        # modules = [data for data in datas] # No need

        for mod in list(datas):

            options += self.get_opt_available(datas[mod])

        return options

    def get_opt_available(self, options):
        """Return Available Options"""

        available_options = []

        for opt in options.keys():

            if not options[opt]:
                continue

            if type(options[opt]) == 'str':

                if options[opt].isdigit():

                    options[opt] = float(options[opt])

            if self.isfloat(options[opt]) or self.isint(options[opt]) or opt in [
                    'AntennaStatus', 'TxMode']:

                available_options.append(opt)

        return available_options

    def get_device_options(self, datas):
        """ Return All Device Options Data """

        tmp = []
        temp = {}

        # modules = [data for data in datas] # No need

        for mod in list(datas):
            tmp.append(datas[mod])

        for dta in tmp:
            temp.update(dta)

        return temp

    def set_select_values(self, datas):
        """Set Select Values"""

        final_data = []

        for data in datas:
            temp = {}
            temp['value'] = data['label']
            temp['label'] = data['label']
            final_data.append(temp)

        return final_data

    def get_stat(self, datas, flag):
        """ Return Min and Max """

        temp = {}
        tmp = []
        if datas:
            if flag is True:
                temp_data = {}

                for data in datas[0].keys():

                    if data != "name":
                        temp_data[data] = tuple(dta[data] for dta in datas)

                # keys = [data for data in temp_data.keys()]
                # for  key in keys:

                #     if all(res is None for res in temp_data[key]):
                #         pass
                #     else:
                #         data = self.get_stat_range(temp_data, key)
                #         temp.update({
                #             key : data
                #         })

                for dta in temp_data.values():
                    tmp += dta

                if tmp:
                    tmp = [dta for dta in tmp if dta is not None]
                    tmp = sorted(tmp, key=float)
                    data = self.get_stat_range(tmp)

                    temp.update({
                        "combine" : data
                    })
            else:
                # keys = [data for data in datas.keys()]

                for key in list(datas.keys()):

                    result = [data[key] for data in datas[key] if data[key] is not None]
                    result = sorted(result, key=float)
                    # if all(res is None for res in result):
                    #     pass
                    # else:
                    if result:
                        data = self.get_stat_range(result)

                        temp.update({
                            key : data
                        })

        return temp

    def get_stat_range(self, data):
        """ Return Stat Range """
        tmp = {}

        tmp['min'] = data[0]
        tmp['max'] = data[-1]
        # tmp['min'] = min(data)
        # tmp['max'] = max(data)

        return tmp
