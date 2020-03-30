# pylint: disable=no-self-use, too-many-statements, too-many-branches, too-many-nested-blocks, too-many-locals, bare-except
"""Email Vessel Info"""
import json
import copy
from datetime import datetime
from datetime import timedelta
import time
import re
import pytz

from library.postgresql_queries import PostgreSQL
from library.common import Common
from library.emailer import Email
from library.couch_queries import Queries
from templates.vessel_report import VesselReport

class EmailVesselInfo(Common):
    """Class for EmailVesselInfo"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for EmailVesselInfo class"""

        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.epoch_default = 26763
        super(EmailVesselInfo, self).__init__()

    def email_vessel_info(self):
        """Email Vessel Information"""

        # DONE EMAIL ID's
        email_ids = self.get_done_email_ids()

        # GET ALL ID's TO EMAIL
        email_schedules = self.get_email_schedule_ids(email_ids)

        for email_schedule in email_schedules or []:

            # SEND EMAIL
            self.email_sender(email_schedule)

        return 1

    def get_done_email_ids(self):
        """Return Done Email IDs"""

        # GET CURRENT UTC DATE
        utc_date = datetime.utcnow().strftime("%Y%m%d")

        # INIT SQL QUERY
        sql_str = "SELECT email_schedule_id FROM email_log"
        sql_str += " WHERE date_today=" + str(utc_date)

        # FETCH ALL
        res = self.postgres.query_fetch_all(sql_str)

        # RETURN
        return res

    def get_email_schedule_ids(self, email_ids):
        """Return Email Schedule IDs"""

        # SET TIME FORMAT
        time_format = '%H:%M:%S'

        # SET GET UTC DATE
        utc_date = datetime.now(tz=pytz.utc)

        # GET UTC TIME
        new_time = utc_date.strftime(time_format)

        # SPLIT TIME
        new_time = new_time.split(":")

        # SET DELTA TIME
        tdel = timedelta(
            hours=int(new_time[0]),
            minutes=int(new_time[1]),
            seconds=int(new_time[2])
        )

        # GET TOTAL SECONDS
        td_seconds = tdel.total_seconds()

        # INIT SQL QUERY
        cols = 'email_vessel_id, email_schedule_id, schedule'
        sql_str = "SELECT " + cols + " FROM email_schedule"
        sql_str += " WHERE utc_time<= " + str(td_seconds)

        # CHECK IF ANY OLD SEND EMAIL ID's
        if email_ids:
            email_ids = [x['email_schedule_id'] for x in email_ids]
            # CEHCK LENTH OF OLD SEND EMAIL ID's
            if len(email_ids) == 1:

                # ADD CONDITION FOR SQL QUERY
                sql_str += " AND email_schedule_id != " + str(email_ids[0])

            else:

                # ADD CONDITION FOR SQL QUERY
                sql_str += " AND email_schedule_id NOT IN " + str(tuple(email_ids))

        # FETCH ALL
        res = self.postgres.query_fetch_all(sql_str)

        # RETURN
        return res

    def email_sender(self, email_schedule):
        """Email Sender"""

        # INIT SQL QUERY
        cols = 'vessel_id, email'
        sql_str = "SELECT " + cols + " FROM email_vessel"
        sql_str += " WHERE mail_enable=true AND email_vessel_id="
        sql_str += str(email_schedule['email_vessel_id'])

        # FETCH ONE
        res = self.postgres.query_fetch_one(sql_str)

        if res:
            vessel_id = res['vessel_id']

            sql_str = "SELECT * FROM report_temp WHERE vessel_id = '" + str(vessel_id) + "'"

            report_temp_res = self.postgres.query_fetch_one(sql_str)

            if report_temp_res:

                report_data = report_temp_res['report_data']
                report_data = report_data.splitlines()

            else:

                report_data = "General Info: \n"
                report_data += """VESSEL: *["PARAMETERS"]["INFO"]["VESSELNAME"]*\n"""
                report_data += "TIME: *TIMESTAMP*\n"
                report_data = report_data.split("\\n")

            pattern = r"\*(.*)\*"

            last_update = self.get_last_update_with_option(vessel_id)
            epoch_time = int(time.time())

            final_data = []

            for line in report_data:
                match = None
                temp_data = {}
                str_line = line
                for match in re.finditer(pattern, line):
                    start_match = match.start()
                    end_match = match.end()

                    pat = r"[a-zA-Z0-9_ ]+"
                    device = re.findall(pat, line[start_match:end_match])

                    if device[0].upper() in ['TIME', 'TIMESTAMP']:

                        pass

                    else:

                        temp_data['label'] = str_line.split(":")[0]

                        values = self.couch_query.get_complete_values(
                            vessel_id,
                            device[0]
                        )
                        if values:
                            try:

                                temp_data['value'] = values[device[0]][device[1]][device[2]]

                            except:

                                temp_data['value'] = ""

                            final_data.append(temp_data)

                        else:

                            temp_data['value'] = ""
                            final_data.append(temp_data)

                if str_line.split(":")[0].upper() == 'STATUS':

                    status = "Offline"
                    if self.check_time_lapse(epoch_time, last_update) == "green":
                        status = "Online"

                    temp_data['label'] = 'STATUS'
                    temp_data['value'] = status
                    final_data.append(temp_data)

                elif match is None:

                    temp_data['label'] = str_line.split(":")[0]
                    temp_data['value'] = ""
                    final_data.append(temp_data)

            temp_message = copy.deepcopy(final_data)

            utc = datetime.utcfromtimestamp(last_update).strftime('%A, %d %B %Y %I:%M:%S %p')
            last_date = utc + " UTC"

            values = self.couch_query.get_complete_values(
                vessel_id,
                "PARAMETERS"
            )

            email = res['email']
            email_temp = VesselReport()
            emailer = Email()

            message = email_temp.vessel_report_temp(final_data, last_date)
            subject = "Scheduled Reporting Event - " + values['PARAMETERS']['INFO']['VESSELNAME']

            emailer.send_email(email, message, subject)
            date_today = datetime.utcnow().strftime("%Y%m%d")

            # INIT NEW VESSEL EMAIL
            temp = {}
            temp['email_schedule_id'] = email_schedule['email_schedule_id']
            temp['email_vessel_id'] = email_schedule['email_vessel_id']
            temp['message'] = json.dumps(temp_message)
            temp['data_date'] = last_date
            temp['date_today'] = date_today
            temp['update_on'] = time.time()
            temp['created_on'] = time.time()

            # INSERT NEW VESSEL EMAIL
            self.postgres.insert('email_log', temp)

        else:

            return 0

        return 1

    # LATE UPDATE WITH OPTION
    def get_last_update_with_option(self, vessel_id):
        """Return Last Updated with Option"""

        values = self.couch_query.get_complete_values(
            vessel_id,
            "COREVALUES",
            flag='one_doc'
        )

        if values:
            return values['timestamp']
        return 0

    def get_device(self, devices, pattern):
        """Return Device"""

        data = []
        for device in devices:

            if re.findall(r'' + pattern + r'\d', device['doc']['device']):
                data.append(device['doc'])

        data = sorted(data, key=lambda i: i['device'])

        return data
