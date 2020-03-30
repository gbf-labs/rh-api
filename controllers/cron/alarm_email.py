# pylint: disable=no-self-use, too-many-locals, too-many-statements, bare-except, invalid-sequence-index
"""Alarm Record"""
import time
import json
from datetime import datetime
from library.log import Log
from library.common import Common
from library.couch_queries import Queries
from library.alarm import calculate_alarm_trigger
from library.alarm import calculate_alarm_value
from library.postgresql_queries import PostgreSQL
from library.alarm.format_alarm_state import FormatAlarmState
from library.emailer import Email
from templates.alarm import Alarm

class AlarmEmail(Common):
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
        super(AlarmEmail, self).__init__()

    def run(self):
        """Run Alarm Trigger"""

        ats = self.get_alarm_trigger()

        for atrigger in ats:

            at_id = atrigger['alarm_trigger_id']
            vessel_ids = self.get_triggered_vessel(at_id)

            for vessel_id in vessel_ids:
                print("Vessel ID: ", vessel_id)
                self.check_alarm(vessel_id, at_id, atrigger)


    def check_alarm(self, vessel_id, trigger_id, adata):
        """ Check Alarm """

        etime = time.time()
        stime = self.timediff_update(etime, 8, key="hours")

        alarm = self.calc_trigger.calculate_trigger([trigger_id], stime, etime, vessel_id)
        data = {}
        if alarm:

            alarm_result = alarm[0]['results']
            if alarm_result and not alarm[0]['err_message']:

                current = self.format_alarm.get_current_alarm(alarm_result)
                current_status = current['datas'][0]['message']
                timestamp = current['datas'][0]['timestamp']
                alarm_occured = time.strftime('%d %b %Y %H:%M:%S',
                                              time.localtime(float(timestamp)))

                email = ", ".join([adata['email']])
                data['subject'] = adata['description']
                data['label'] = adata['label']
                data['alarm_type'] = adata['alarm_type']
                data['timestamp'] = alarm_occured
                data['details'] = alarm_result
                data['status'] = current_status
                # CHECK ALARM EMAIL TABLE LAST STATUS
                prev_status = self.check_previous_alarm(vessel_id, trigger_id)
                date_today = datetime.utcnow().strftime("%Y%m%d")

                previous_status = ""
                send_email = ""

                if prev_status:

                    previous_status = prev_status['alarm_status']
                    if prev_status['epoch_date'] != int(date_today):

                        if current_status.upper() == "ALARM":
                            # SEND EMAIL
                            data['message'] = "{0} status has been changed.".format(adata['label'])
                            send_email = self.send_alarm_email(email, data)
                    else:

                        if previous_status.upper() != current_status.upper():
                            data['message'] = "{0} status has been changed.".format(adata['label'])
                            # SEND EMAIL
                            send_email = self.send_alarm_email(email, data)
                else:
                    if current_status.upper() == "ALARM":

                        # SEND EMAIL
                        data['message'] = "{0} status has been changed.".format(adata['label'])
                        send_email = self.send_alarm_email(email, data)

                # ADD LOG TO ALARM EMAIL

                if send_email:

                    temp = {}
                    temp['alarm_trigger_id'] = trigger_id
                    temp['vessel_id'] = vessel_id
                    temp['device_id'] = alarm_result[0]['device_id']
                    temp['alarm_status'] = current_status
                    temp['message'] = json.dumps(data)
                    temp['epoch_date'] = date_today
                    temp['update_on'] = time.time()
                    temp['created_on'] = time.time()

                    # INSERT NEW VESSEL EMAIL
                    self.postgres.insert('alarm_email', temp)
                    print("Log Added")
        return 1

    def check_previous_alarm(self, vessel_id, alarm_trigger_id):
        """ Return Previous Alarm Status """

        sql_str = "SELECT * FROM alarm_email"
        sql_str += " WHERE vessel_id = '{0}'".format(vessel_id)
        sql_str += " AND alarm_trigger_id = '{0}'".format(alarm_trigger_id)
        sql_str += " ORDER BY created_on DESC"
        result = self.postgres.query_fetch_one(sql_str)

        return result

    def get_alarm_trigger(self):
        """Return Alarm Triggers"""

        sql_str = "SELECT atr.*, aty.alarm_type FROM alarm_trigger atr"
        sql_str += " LEFT JOIN alarm_type aty ON atr.alarm_type_id = aty.alarm_type_id"
        sql_str += " WHERE atr.alarm_enabled=true AND alarm_email=true"

        res = self.postgres.query_fetch_all(sql_str)

        return res

    def get_triggered_vessel(self, at_id):
        """Return Triggered Vessel"""

        sql_str = "SELECT * FROM alarm_condition WHERE alarm_condition_id IN ("
        sql_str += " SELECT alarm_condition_id FROM alarm_trigger WHERE"
        sql_str += " alarm_trigger_id={0})".format(at_id)

        alarm_condition = self.postgres.query_fetch_one(sql_str)

        # av_ids = list({x['id'] for x in alarm_condition['parameters'] if 'id' in x.keys()})

        prmtr_ids = set()

        for prmtr in alarm_condition['parameters']:

            if 'id' in prmtr.keys():

                if prmtr['id']:

                    prmtr_ids.add(prmtr['id'])

        av_ids = list(prmtr_ids)

        # DATA
        sql_str = "SELECT * FROM alarm_value"
        sql_str += " WHERE alarm_value_id in ({0})".format(','.join(map(str, av_ids)))
        alarm_value = self.postgres.query_fetch_all(sql_str)

        arr_vessels_id = []
        arr_options = []
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

    def send_alarm_email(self, email, data):
        """Send Invitation"""

        if not email:
            return 0

        email_temp = Alarm()
        emailer = Email()

        message = email_temp.alarm_temp(data)
        subject = "Alarm - {0}".format(data['subject'])
        send = emailer.send_email(email, message, subject)

        if send:
            return 1
        return 0
