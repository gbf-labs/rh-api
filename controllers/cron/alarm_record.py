# pylint: disable=no-self-use, too-many-locals, too-many-statements, bare-except, unidiomatic-typecheck, too-many-arguments, invalid-sequence-index
"""Alarm Record"""
import time
import json
from library.log import Log
from library.common import Common
from library.couch_queries import Queries
from library.alarm import calculate_alarm_trigger
from library.alarm import calculate_alarm_value
from library.postgresql_queries import PostgreSQL
from library.alarm.format_alarm_state import FormatAlarmState

class AlarmRecord(Common):
    """Class for AlarmRecord"""

    def __init__(self):
        """The Constructor for AlarmRecord class"""
        self.postgres = PostgreSQL()
        self.log = Log()
        self.calc_trigger = calculate_alarm_trigger.CalculateAlarmTrigger()
        self.calc_value = calculate_alarm_value.CalculateAlarmValue()
        self.format_alarm = FormatAlarmState()
        self.couch_query = Queries()
        self.epoch_default = 26763
        super(AlarmRecord, self).__init__()

    def run(self):
        """Run Alarm Trigger"""

        ats = self.get_alarm_trigger()

        if ats:
            for atrigger in ats:

                current_date = self.epoch_day(time.time())

                epoch_time = self.days_update(current_date)
                epoch_time -= 1

                at_id = atrigger['alarm_trigger_id']

                vessel_ids = self.get_triggered_vessel(at_id)

                for vessel_id in vessel_ids:

                    # last_update = self.get_last_update(at_id, vessel_id, st, epoch_time)

                    self.update_alarm_data(at_id, vessel_id, epoch_time)
        else:
            print("No Alarm Trigger Available")

    def get_alarm_trigger(self):
        """Return Alarm Triggers"""

        sql_str = "SELECT * FROM alarm_trigger WHERE alarm_enabled=true"

        res = self.postgres.query_fetch_all(sql_str)

        return res

    def get_alarm_param(self, condition_id):
        """ Return Alarm Condition Parameter """
        sql_str = "SELECT * FROM alarm_condition"
        sql_str += " WHERE alarm_condition_id={0}".format(condition_id)

        param_id = set()
        alarm_condition = self.postgres.query_fetch_one(sql_str)

        if alarm_condition:

            for param in alarm_condition['parameters']:
                if 'id' in param.keys():
                    param_id.add(param['id'])

        return param_id

    def get_triggered_vessel(self, at_id):
        """Return Triggered Vessel"""

        sql_str = "SELECT * FROM alarm_condition WHERE alarm_condition_id IN ("
        sql_str += " SELECT alarm_condition_id FROM alarm_trigger WHERE"
        sql_str += " alarm_trigger_id={0})".format(at_id)

        alarm_condition = self.postgres.query_fetch_one(sql_str)

        # av_ids = list({x['id'] for x in alarm_condition['parameters'] if 'id' in x.keys()})

        prmtr_ids = set()
        prmtr_conditions = []
        for prmtr in alarm_condition['parameters']:

            if 'id' in prmtr.keys():

                if prmtr['id']:
                    if prmtr['type'] == "values":
                        prmtr_ids.add(prmtr['id'])
                    if prmtr['type'] == "conditions":

                        prmtr_conditions += self.get_alarm_param(prmtr['id'])

        av_ids = list(prmtr_ids) + prmtr_conditions

        # DATA
        sql_str = "SELECT * FROM alarm_value"
        sql_str += " WHERE alarm_value_id in ({0})".format(','.join(map(str, av_ids)))

        alarm_value = self.postgres.query_fetch_all(sql_str)

        arr_vessels_id = []
        arr_options = []

        if alarm_value:

            for avalue in alarm_value:

                if arr_vessels_id:

                    for vessel_id in avalue['vessel'].split(","):
                        arr_vessels_id.append(vessel_id)

                    for opt in avalue['option'].split(","):
                        arr_options.append(opt)
                    # options.append(av['option'].split(","))

                else:

                    arr_vessels_id = avalue['vessel'].split(",")
                    arr_options = avalue['option'].split(",")

        vessels_id = ','.join(map(str, arr_vessels_id))
        options = ','.join(map(str, arr_options))

        vessels_ids = self.calc_value.get_all_vessels(vessels_id, options)

        return vessels_ids

    def update_alarm_data(self, at_id, vessel_id, epoch_time):
        """Update Alarm Data"""

        sql_str = "SELECT epoch_date FROM alarm_data WHERE "
        sql_str += "vessel_id='{0}' AND ".format(vessel_id)
        sql_str += "alarm_trigger_id={0} ".format(at_id)
        sql_str += "ORDER BY epoch_date DESC LIMIT 1"
        epoch_date = self.postgres.query_fetch_one(sql_str)

        timestamp = 0
        if epoch_date:

            timestamp = epoch_date['epoch_date']

        else:

            self.log.low("NEW ALARM RECORD!")
            values = self.couch_query.get_complete_values(
                vessel_id,
                "COREVALUES",
                start=str(9999999999),
                end=str(self.epoch_default),
                flag='one_doc',
                descending=False
            )
            timestamp = values['timestamp']

        late_et = self.days_update(timestamp, 1, True)
        late_st = self.days_update(late_et, 1)

        # late_et -= 1

        new_et = late_et

        while int(new_et) <= int(epoch_time):

            current_time = time.time()
            late_et = self.days_update(late_et, 1, True)
            late_st = self.days_update(late_et, 1)

            if late_st > epoch_time:

                break

            new_et = late_et - 1
            alarm = self.calc_trigger.calculate_trigger([at_id], late_st, late_et, vessel_id)

            alarm_index_0 = ""

            try:

                alarm_index = alarm[0]['results']
                alarm_index_0 = alarm_index[0]
                vessel_name = alarm_index_0['vessel_name']
                vessel_number = alarm_index_0['vessel_number']
                alarm_datas = alarm_index_0['datas']

                # COMPUTE PERCENTAGE
                green, orange, red, blue, violet = self.get_alarm_percentage(alarm_datas)

                average = {}
                average['green'] = green
                average['orange'] = orange
                average['red'] = red
                average['blue'] = blue
                average['violet'] = violet

                module = ""

                if 'module' in alarm_index_0.keys():
                    module = alarm_index_0['module']

                option = ""

                if 'option' in alarm_index_0.keys():
                    option = alarm_index_0['option']

                # SAVE TO ALARM DATA
                data = {}
                data["alarm_trigger_id"] = at_id
                data["average"] = json.dumps(average)
                data["device"] = alarm_index_0['device']
                data["module"] = module
                data["option"] = option
                data["vessel_id"] = vessel_id
                data["vessel_name"] = vessel_name
                data["vessel_number"] = vessel_number
                data["alarm_type_id"] = alarm[0]['alarm_type_id']
                data["epoch_date"] = int(late_st)
                data["created_on"] = current_time
                data["update_on"] = current_time
                data["alarm_description"] = alarm[0]['alarm_description']
                data["err_message"] = alarm[0]['err_message']
                data["device_id"] = alarm_index_0['device_id']
                data["message"] = alarm_index_0['message']
                data["alarm_type"] = alarm[0]['alarm_type']

                self.postgres.insert('alarm_data', data)

                late_et += 1

            except:

                return 1

    def get_alarm_percentage(self, datas):
        """Return Alarm Percentage"""

        green = 0
        orange = 0
        red = 0
        blue = 0
        violet = 0
        for data in datas:

            if data['remarks'] == 'green':

                green += 1

            elif data['remarks'] == 'orange':

                orange += 1

            elif data['remarks'] == 'red':

                red += 1

            elif data['remarks'] == 'blue':

                blue += 1

            elif data['remarks'] == 'violet':

                violet += 1

        # COUMPUTE
        if datas:

            green = green * 100 / len(datas)
            orange = orange * 100 / len(datas)
            red = red * 100 / len(datas)
            blue = blue * 100 / len(datas)
            violet = violet * 100 / len(datas)

        else:

            violet = 100

        return [green, orange, red, blue, violet]

    def run_current_alarm(self):
        """ RUN CURRENT ALARM """

        self.run_alarm_state()
        return 1

    def run_day_alarm(self):
        """ RUN 24 HOURS ALARM """
        self.run_alarm_state("day")
        return 1

    # ALARM FOR CURRENT STATE AND 24 HOURS
    def run_alarm_state(self, epoch_format=""):
        """ RUN ALARM FOR CURRENT STATE """

        atriggers = self.get_alarm_trigger()

        if epoch_format == "day":
            key = epoch_format
            start = 1

        else:
            key = "hours"
            start = 8

        end_time = time.time()
        start_time = self.timediff_update(end_time, start, key=key)
        late_et = self.days_update(end_time, 1, True)
        late_st = self.days_update(late_et, 1)

        for atrigger in atriggers:

            at_id = atrigger['alarm_trigger_id']

            vessel_ids = self.get_triggered_vessel(at_id)

            for vessel_id in vessel_ids:
                print("Key: {0} Alarm Vessel ID: {1}".format(key, vessel_id))
                datas = self.calc_trigger.calculate_trigger(
                    [at_id],
                    start_time,
                    end_time,
                    vessel_id=vessel_id
                )

                if type(datas) == list:

                    datas = self.get_datas(datas, epoch_format, end_time)

                    if not epoch_format:
                        datas = self.format_alarm.filter_current_status(datas)
                else:
                    pass

                # INSERT OR UPDATE TO TABLE
                if datas[0]['results']:

                    self.add_alarm_state(vessel_id, at_id, late_st, datas, key)
                else:
                    pass

    def get_datas(self, datas, epoch_format, end_time):
        """ Set datas """

        for alarm in datas:
            alarm_result = alarm['results']

            if alarm_result and not alarm['err_message']:
                if not epoch_format:
                    self.format_alarm.get_current_alarm(alarm_result)

                else:
                    self.format_alarm.get_alarm24(alarm_result, end_time)

        return datas

    def add_alarm_state(self, vessel_id, at_id, epoch_date, result, key):
        """ Add or Insert Alarm State """

        # CHECK IF DATA EXIST ON CURRENT DATE

        sql_str = "SELECT * FROM alarm_state"
        sql_str += " WHERE alarm_trigger_id='{0}' AND vessel_id='{1}'".format(at_id, vessel_id)
        sql_str += " AND epoch_date='{0}' AND category='{1}'".format(int(epoch_date), key)
        state = self.postgres.query_fetch_one(sql_str)

        current_time = time.time()
        res = result[0]['results']
        data = {}
        if not state:

            # INSERT TO ALARM STATE
            data["alarm_trigger_id"] = at_id
            data["category"] = key
            data["results"] = json.dumps(res)
            data["device"] = res[0]['device']
            data["module"] = res[0]['module']
            data["option"] = res[0]['option']
            data["vessel_id"] = res[0]['vessel_id']
            data["vessel_name"] = res[0]['vessel_name']
            data["alarm_description"] = result[0]['alarm_description']
            data["err_message"] = result[0]['err_message']
            data["device_id"] = res[0]['device_id']
            data["message"] = res[0]['message']
            data["alarm_type"] = result[0]['alarm_type']
            data["vessel_number"] = res[0]['vessel_number']
            data["alarm_type_id"] = result[0]['alarm_type_id']
            data["epoch_date"] = int(epoch_date)
            data["created_on"] = current_time
            data["update_on"] = current_time

            self.postgres.insert('alarm_state', data)

        else:

            # UPDATE ALARM STATE
            data['results'] = json.dumps(res)
            data['update_on'] = current_time
            data["err_message"] = result[0]['err_message']
            data["message"] = res[0]['message']
            conditions = []

            conditions.append({
                "col": "alarm_state_id",
                "con": "=",
                "val": state['alarm_state_id']
            })

            self.postgres.update('alarm_state', data, conditions)

        return 1
