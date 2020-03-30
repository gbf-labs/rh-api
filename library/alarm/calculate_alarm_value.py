# pylint: disable=no-self-use, too-many-arguments, too-many-locals, too-many-branches, bare-except
"""Calculate Alarm Value"""
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries

class CalculateAlarmValue(Common):
    """Class for CalculateAlarmValue"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CalculateAlarmValue class"""

        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(CalculateAlarmValue, self).__init__()

    def calculate_value(self, alarm_value_id, start, end, vessel_id=None, device_id=None):
        """Calculate Alarm Value"""

        if alarm_value_id:

            results = []
            alarm_value = self.get_alarm_value(alarm_value_id)

            if alarm_value:

                vessels = alarm_value['vessel']
                devices = alarm_value['device']
                device_types = alarm_value['device_type']
                modules = alarm_value['module']
                options = alarm_value['option']


                #VALIDATE VESSEL IF EXISTS IN ALARM VALUE
                if vessel_id:
                    vessel = self.validate_alarm_vessel(vessels, vessel_id)

                    if vessel:
                        vessel_list = [vessel]
                    else:

                        #RETURN NO DATA TO SHOW
                        return 0
                else:
                    vessel_list = self.get_all_vessels(vessels, options)

                #GET DATA
                for vessel in vessel_list:

                    #VALIDATE DEVICE IF EXISTS IN ALARM VALUE
                    if device_id:
                        device = self.validate_alarm_device(vessel, devices, device_id)

                        if device:
                            device_list = [device]
                        else:
                            return 0
                    else:
                        device_list = self.find_device_by_type(vessel, devices, device_types)

                    #GET COREVALUES AND PREVIOUS COREVALUES DATA
                    corevalues = self.couch_query.get_coredata(vessel, start, end)
                    prev_core = self.get_previous_coremarks(vessel, start)

                    for device in device_list:

                        modlist = self.find_alarm_data(vessel, modules, key="module")
                        optlist = self.find_alarm_data(vessel, options, key="option")

                        # GET DATA ON COUCHDB BY VESSEL AND DEVICE
                        datas = self.get_vessel_data(vessel, device, start, end)

                        if datas:

                            mod_data = self.get_mod_data(device, modlist, datas)
                            opt_data = self.get_option_data(device, mod_data, optlist, datas)

                            results += self.set_opt_values(opt_data,
                                                           vessel,
                                                           corevalues,
                                                           prev_core,
                                                           device)

                        else:

                            mod_option = self.get_mod_opt(vessel, device, corevalues,
                                                          prev_core, modlist, optlist)
                            results += mod_option

            return results

        return 0

    def get_previous_coremarks(self, vessel, end):
        """Get Previous Corevalues Remarks"""

        data = {}
        corevalues = self.couch_query.get_coredata(vessel, 0, end, flag="limit")

        if corevalues:
            data['timestamp'] = corevalues[0]
            data['remarks'] = "Unknown"

        else:
            data['timestamp'] = ""
            data['remarks'] = "No Data"

        return data

    def find_alarm_data(self, vessel, datas, key):
        """Find Alarm Values Data"""

        temp_data = []

        if datas:

            #CHECK INPUTS IF EXIST IN VESSEL
            for data in datas.split(","):

                check_data = self.check_data_by_vessel(key, vessel, data)

                if check_data:

                    for cdata in check_data:

                        temp_data.append(cdata[key])

        else:

            #GET ALL DEVICES IF NO VESSELS
            datas = self.check_data_by_vessel(key, vessel)

            for data in datas:
                temp_data.append(data[key])

        return temp_data


    # GET ALARM VALUE
    def get_alarm_value(self, alarm_value_id):
        """Get Alarm Value"""

        assert alarm_value_id, "Alarm value ID is required."

        # DATA
        sql_str = "SELECT * FROM alarm_value"
        sql_str += " WHERE alarm_value_id={0}".format(alarm_value_id)
        alarm_value = self.postgres.query_fetch_one(sql_str)

        if alarm_value:

            return alarm_value

        return 0

    def get_all_vessels(self, vessels, options):
        """Get All Vessels"""

        vessel_list = []

        if vessels:

            tmp_vessel = []
            for vessel in vessels.split(","):
                tmp_vessel.append(vessel)

            vessel_ids = ','.join(["'{}'".format(tmp) for tmp in tmp_vessel])

            sql_str = "SELECT vessel_id FROM vessel"
            sql_str += " WHERE vessel_id IN ({0})".format(vessel_ids)

            datas = self.postgres.query_fetch_all(sql_str)

            vessel_list = [data['vessel_id'] for data in datas]

        else:

            #OPTION IS REQUIRED ON ALARM VALUE
            vessel_list = self.get_vessels_by_option(options)
        return vessel_list


    def get_vessels_by_option(self, options):
        """Get Vessels By Option"""

        datas = ""

        if options:

            tmp_opt = []
            for option in options.split(","):
                tmp_opt.append(option)

            opt = ','.join(["'{}'".format(tmp) for tmp in tmp_opt])


            # OPTION DATA
            sql_str = "SELECT DISTINCT vessel_id FROM option"
            sql_str += " WHERE option IN ({0})".format(opt)

            datas = self.postgres.query_fetch_all(sql_str)

        if datas:
            vessel_list = [data['vessel_id'] for data in datas]

        else:
            vessel_list = self.vessel_list()

        return vessel_list

    def vessel_list(self):
        """Get Vessel List"""

        sql_str = "SELECT vessel_id FROM vessel"

        datas = self.postgres.query_fetch_all(sql_str)

        if datas:
            vessel_list = [data['vessel_id'] for data in datas]

        return vessel_list

    def get_vessel_data(self, vessel, device, start_time, end_time):
        """Get Vessel Data"""

        if vessel:

            values = self.couch_query.get_complete_values(
                vessel,
                device,
                str(start_time),
                str(end_time),
                'all')

            if values:

                return values

        return 0


    # GET DATA DEVICE/MODULE/OPTION
    def check_data_by_vessel(self, key, vessel_id, value=None):
        """Check Alarm Data by Vessel"""

        if key == "device_type":
            table = "device"

        else:
            table = key

        # DATA
        sql_str = "SELECT DISTINCT {0} FROM {1}".format(key, table)
        sql_str += " WHERE vessel_id ='{0}'".format(vessel_id)

        if value:
            sql_str += " AND {0} ILIKE '{1}'".format(key, value.strip())

        datas = self.postgres.query_fetch_all(sql_str)

        if datas:

            return datas

        return ''

    def get_mod_data(self, device, modules, datas):
        """Filter modules by vessel's alarm data"""

        temp_data = []

        for module in modules:

            alarm_data = [module for data in datas if module in data['value'][device]]
            temp_data += alarm_data

        return set(temp_data)

    def get_option_data(self, device, modules, options, datas):
        """Get option by vessel's alarm data"""

        temp_data = []
        results = []

        for module in modules:
            for option in options:

                if option in datas[0]['value'][device][module]:

                    message = "ok"
                    for data in datas:
                        temp_data.append({
                            "timestamp": data['timestamp'],
                            "value": data['value'][device][module][option]
                        })
                else:

                    message = "No option {0} found under module".format(option)

                results.append({
                    "device": device,
                    "module": module,
                    "option": option,
                    "datas": temp_data,
                    "message": message
                })

        return results

    def get_mod_opt(self, vessel, device, core, prev_core, modules, options):
        """Get Module Option if no data found per vessel"""

        results = []
        module = "No Module found"
        option = "No Option found"

        for module in modules:

            if options:
                # Miss Ly, May something dito.
                # for option in options:
                    # option = option
                option = options[-1]

            results.append({
                "vessel_id": vessel,
                "device": device,
                "device_id": self.get_device_id(vessel, device),
                "module": module,
                "option": option,
                "datas":  [],
                "message": "No Data",
                "core": core,
                "previous": prev_core
                })

        return results


    def find_device_by_type(self, vessel, devices, device_types):
        """Find Device"""

        check_device = self.find_alarm_data(vessel, devices, key="device")

        if device_types:

            device_list = []
            devicetype_list = self.find_alarm_data(vessel, device_types, key="device_type")

            if devices:

                for device in check_device:

                    try:
                        device_index = devicetype_list.index(device)
                        device_list.append(devicetype_list[device_index])
                    except:
                        device_list.append(device)
            else:

                device_list = devicetype_list

        else:
            device_list = check_device

        return device_list

    def get_device_by_id(self, device_id):
        """Get Device by ID"""

        # DATA
        sql_str = "SELECT DISTINCT device FROM device"
        sql_str += " WHERE device_id = '{0}'".format(device_id)

        data = self.postgres.query_fetch_one(sql_str)

        if data:

            return data['device']

        return ''

    def get_device_id(self, vessel_id, device):
        """Get Device ID"""

        # DATA
        sql_str = "SELECT DISTINCT device_id FROM device"
        sql_str += " WHERE device = '{0}'".format(device)
        sql_str += " AND vessel_id ='{0}'".format(vessel_id)

        data = self.postgres.query_fetch_one(sql_str)

        if data:

            return data['device_id']

        return ''

    def validate_alarm_device(self, vessel, devices, device_id):
        """Validate Alarm Device"""

        #IF EMPTY DEVICES IT SELECTED ALL DEVICES
        device = self.get_device_by_id(device_id)

        device_list = self.find_alarm_data(vessel, devices, key="device")

        if device in device_list:

            return device

        return 0

    def validate_alarm_vessel(self, vessels, vessel_id):
        """Validate Alarm Vessel"""

        #IF EMPTY VESSELS IT SELECTED ALL VESSELS
        if vessels:

            vessel_list = []
            for vessel in vessels.split(","):
                vessel_list.append(vessel)

            if vessel_id in vessel_list:
                return vessel_id

            return 0

        return vessel_id

    def set_opt_values(self, datas, vessel, corevalues, prev_core, device):
        """ Set Option values """

        res = []

        for option in datas:
            option['vessel_id'] = vessel
            option['core'] = corevalues
            option['previous'] = prev_core
            option['device_id'] = self.get_device_id(vessel, device)

            res.append(option)

        return res
