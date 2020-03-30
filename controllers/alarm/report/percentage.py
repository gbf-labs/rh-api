# pylint: disable=too-many-locals, too-many-arguments, line-too-long, too-many-statements, too-many-branches, too-many-nested-blocks, invalid-sequence-index
"""Alarm Report Percentage"""
import time

from library.log import Log
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm import calculate_alarm_trigger
from controllers.cron.alarm_record import AlarmRecord

class Percentage(Common):
    """Class for Percentage"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Percentage class"""

        self.log = Log()
        self.postgres = PostgreSQL()
        self.alarm_record = AlarmRecord()
        self.calc_trigger = calculate_alarm_trigger.CalculateAlarmTrigger()
        super(Percentage, self).__init__()

    def report_pecentage(self, verbose_level, v_id, req_format, device_id="", flag=False):
        """Return Report Percentage"""

        data = {}

        alarm_triggers = self.convert_verbose_level(verbose_level, flag)

        final_datas = []
        for alarm_trigger in alarm_triggers:

            final_v_ids = []

            if v_id:

                final_v_ids = [v_id]

            else:

                final_v_ids = self.get_alarm_trigger_v_ids(alarm_trigger['alarm_trigger_id'])

            final_data_temp = []

            alarm_description = ""
            at_id = ""
            alarm_type = ""
            err_message = ""
            alarm_type_id = ""
            # START COLLECT DATA
            for vessel_id in final_v_ids:


                at_id = alarm_trigger['alarm_trigger_id']
                alarm_type_id = alarm_trigger['alarm_type_id']

                current = self.days_update(time.time())
                start_date = 0

                if req_format.lower() == "week":

                    start_date = self.days_update(time.time(), 7)

                elif req_format.lower() == "month":

                    start_date = self.datedelta(time.time(), days=1, months=1)

                elif req_format.lower() in ["annual", "quarter"]:

                    start_date = self.datedelta(time.time(), days=1, years=1)


                if req_format.lower() in ["annual", "quarter"]:

                    rng = 12
                    if req_format.lower() == "quarter":
                        rng = 3

                    new_current = current

                    # INIT VARIABLE
                    message = ""

                    device = ""
                    module = ""
                    option = ""
                    vessel_name = ""
                    vessel_number = ""

                    arry_average = []
                    for _ in range(0, rng):

                        green = 0
                        orange = 0
                        red = 0
                        blue = 0
                        violet = 0

                        start_date = self.datedelta(new_current, months=1)

                        alarms = self.get_alarm_data(
                            vessel_id,
                            at_id,
                            start_date,
                            new_current,
                            device_id,
                            flag
                            )

                        if alarms:

                            for als in [alarm['average'] for alarm in alarms]:

                                green += als['green']
                                orange += als['orange']
                                red += als['red']
                                blue += als['blue']
                                violet += als['violet']

                            total_alarm = len(alarms) * 100

                            green = green * 100 / total_alarm
                            orange = orange * 100 / total_alarm
                            red = red * 100 / total_alarm
                            blue = blue * 100 / total_alarm
                            violet = violet * 100 / total_alarm

                            vessel_name = alarms[0]['vessel_name']
                            vessel_number = alarms[0]['vessel_number']
                            device = alarms[0]['device']
                            module = alarms[0]['module']
                            option = alarms[0]['option']

                            alarm_description = alarms[0]['alarm_description']
                            alarm_type = alarms[0]['alarm_type']
                            err_message = alarms[0]['err_message']

                            if green == orange == red == blue == violet == 0:

                                violet = 100

                        # else:

                        #     violet = 100

                            average = {}

                            average['green'] = float("{:.2f}".format(green))
                            average['orange'] = float("{:.2f}".format(orange))
                            average['red'] = float("{:.2f}".format(red))
                            average['blue'] = float("{:.2f}".format(blue))
                            average['violet'] = float("{:.2f}".format(violet))
                            average["start_time"] = int(start_date)
                            average["end_time"] = int(new_current)
                            arry_average.append(average)

                        new_current = start_date

                    data_temp = {}
                    if arry_average:
                        data_temp["datas"] = arry_average
                        data_temp["device_id"] = device_id
                        data_temp["message"] = message
                        data_temp["vessel_id"] = vessel_id
                        data_temp["device"] = device
                        data_temp["module"] = module
                        data_temp["option"] = option
                        data_temp["vessel_name"] = vessel_name
                        data_temp["vessel_number"] = vessel_number

                else:

                    arry_average = []

                    # CURRENT ALARM
                    current_date = self.epoch_day(time.time())
                    s_time = self.days_update(current_date)
                    e_time = self.days_update(current_date, 1, True)

                    e_time -= 1
                    alrm = self.get_current_alarm(at_id, s_time, e_time, vessel_id)

                    data_temp = {}
                    if not alrm['err_message']:
                        f_average = {}
                        f_average['green'] = alrm['average']['green']
                        f_average['orange'] = alrm['average']['orange']
                        f_average['red'] = alrm['average']['red']
                        f_average['blue'] = alrm['average']['blue']
                        f_average['violet'] = alrm['average']['violet']
                        f_average["epoch_date"] = alrm['epoch_date']

                        alrm_status = False
                        if f_average['green'] == f_average['orange'] == f_average['red'] == f_average['blue'] == f_average['violet'] == 0:

                            f_average['violet'] = 100

                        else:

                            alrm_status = True

                        device_id = alrm['device_id']
                        message = alrm['message']
                        device = alrm['device']
                        module = alrm['module']
                        option = alrm['option']
                        vessel_name = alrm['vessel_name']
                        vessel_number = alrm['vessel_number']

                        alarm_description = alrm['alarm_description']
                        alarm_type = alrm['alarm_type']
                        err_message = alrm['err_message']

                        end_date = self.days_update(s_time, 1)

                        while start_date < end_date:
                            # GET ALARM DATA
                            alarms = self.get_alarm_data(vessel_id,
                                                         at_id,
                                                         start_date,
                                                         False,
                                                         device_id,
                                                         flag
                                                        )

                            start_date = self.days_update(start_date, 1, True)

                            if alarms:

                                average = {}
                                average['green'] = alarms[0]['average']['green']
                                average['orange'] = alarms[0]['average']['orange']
                                average['red'] = alarms[0]['average']['red']
                                average['blue'] = alarms[0]['average']['blue']
                                average['violet'] = alarms[0]['average']['violet']
                                average["epoch_date"] = start_date

                                if average['green'] == average['orange'] == average['red'] == average['blue'] == average['violet'] == 0:

                                    average['violet'] = 100

                                arry_average.append(average)
                                alrm_status = True
                            else:

                                average = {}
                                average['green'] = 0
                                average['orange'] = 0
                                average['red'] = 0
                                average['blue'] = 0
                                if alrm_status:
                                    average['orange'] = 100
                                    average['violet'] = 0
                                else:
                                    average['orange'] = 0
                                    average['violet'] = 100

                                average["epoch_date"] = start_date
                                arry_average.append(average)

                        arry_average.append(f_average)

                        arry_average.reverse()

                        data_temp["datas"] = arry_average
                        data_temp["vessel_id"] = vessel_id
                        data_temp["device_id"] = device_id
                        data_temp["message"] = message
                        data_temp["device"] = device
                        data_temp["module"] = module
                        data_temp["option"] = option
                        data_temp["vessel_name"] = vessel_name
                        data_temp["vessel_number"] = vessel_number

                if data_temp:
                    final_data_temp.append(data_temp)

            temp = {}
            temp["alarm_description"] = alarm_description
            temp["alarm_trigger_id"] = at_id
            temp["alarm_type"] = alarm_type
            temp["alarm_type_id"] = alarm_type_id
            temp["err_message"] = err_message
            temp["results"] = final_data_temp

            final_datas.append(temp)

        data['data'] = final_datas
        data['status'] = "ok"
        return self.return_data(data)

    def convert_verbose_level(self, verbose, flag):
        """Return Alarm Trigger ID by verbose level or Alarm Type Value"""

        assert verbose, "Verbose is required."

        # DATA
        sql_str = "SELECT alarm_trigger_id, alarm_type_id FROM alarm_trigger"
        sql_str += " WHERE alarm_type_id IN"
        sql_str += " (SELECT alarm_type_id FROM alarm_type"

        if flag:

            sql_str += " WHERE alarm_value = {0})".format(verbose)

        else:

            sql_str += " WHERE alarm_value <= {0})".format(verbose)

        alarm_types = self.postgres.query_fetch_all(sql_str)

        if alarm_types:

            return alarm_types

        return 0

    def get_alarm_data(self, vessel_id, at_id, start, end, device_id="", flag=False):
        """Return Alarm Data"""

        sql_str = "SELECT * FROM "
        sql_str += "alarm_data WHERE "
        sql_str += "alarm_trigger_id={0} ".format(at_id)

        if end:

            sql_str += "AND epoch_date < {0} ".format(end)
            sql_str += "AND epoch_date > {0} ".format(start)

        else:

            sql_str += "AND epoch_date = {0} ".format(start)

        if vessel_id:

            sql_str += "AND vessel_id='{0}' ".format(vessel_id)

        if flag:

            sql_str += "AND device_id = '{0}' ".format(device_id)

        sql_str += "ORDER BY epoch_date desc"

        alarm_types = self.postgres.query_fetch_all(sql_str)

        if alarm_types:

            return alarm_types

        return 0

    def get_current_alarm(self, atrigger_id, start_time, end_time, vessel_id):
        """Return Current Alarm"""

        # print("atrigger_id: ", atrigger_id)
        # print("start_time: ", start_time)
        # print("end_time: ", end_time)
        # print("vessel_id: ", vessel_id)

        if vessel_id:
            alarm = self.calc_trigger.calculate_trigger([atrigger_id], start_time, end_time, vessel_id)
        else:
            alarm = self.calc_trigger.calculate_trigger([atrigger_id], start_time, end_time)

        alarm_datas = []
        alarm_index_0 = {}

        if len(alarm[0]['results']) != 0:

            alarm_index = alarm[0]['results']
            alarm_index_0 = alarm_index[0]

            v_id = alarm_index_0['vessel_id']
            vessel_name = alarm_index_0['vessel_name']
            vessel_number = alarm_index_0['vessel_number']
            alarm_datas = alarm_index_0['datas']
            device = alarm_index_0['device']
            device_id = alarm_index_0['device_id']
            message = alarm_index_0['message']
        else:
            v_id = vessel_id
            vessel_name = ""
            vessel_number = ""
            device = ""
            device_id = ""
            message = ""

        # COMPUTE PERCENTAGE
        green, orange, red, blue, violet = self.alarm_record.get_alarm_percentage(alarm_datas)

        average = {}
        average['green'] = green
        average['orange'] = orange
        average['red'] = red
        average['blue'] = blue
        average['violet'] = violet

        module = ""
        option = ""

        if alarm_index_0:
            if 'module' in alarm_index_0.keys():
                module = alarm_index_0['module']

            if 'option' in alarm_index_0.keys():
                option = alarm_index_0['option']

        # SAVE TO ALARM DATA
        data = {}
        data["alarm_trigger_id"] = atrigger_id
        data["average"] = average
        data["device"] = device
        data["module"] = module
        data["option"] = option
        data["vessel_id"] = v_id
        data["vessel_name"] = vessel_name
        data["vessel_number"] = vessel_number
        data["alarm_type_id"] = alarm[0]['alarm_type_id']
        data["epoch_date"] = int(start_time)
        data["alarm_description"] = alarm[0]['alarm_description']
        data["err_message"] = alarm[0]['err_message']
        data["device_id"] = device_id


        data["message"] = message
        data["alarm_type"] = alarm[0]['alarm_type']

        return data

    def get_alarm_trigger_v_ids(self, alarm_trigger_id):
        """Return Alarm Trigger Value IDs"""

        sql_str = "SELECT DISTINCT vessel_id FROM alarm_data WHERE "
        sql_str += "alarm_trigger_id={0}".format(alarm_trigger_id)

        vessel_ids = self.postgres.query_fetch_all(sql_str)

        final_v_ids = [x['vessel_id'] for x in vessel_ids]

        return final_v_ids
