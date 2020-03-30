# pylint: disable=too-many-locals
"""Update Email Schedule"""
import time

from datetime import datetime, timedelta
from flask import request
from pytz import timezone
import dateutil.tz

from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdateEmailSchedule(Common):
    """Class for UpdateEmailSchedule"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for UpdateEmailSchedule class"""
        self.postgresql_query = PostgreSQL()
        super(UpdateEmailSchedule, self).__init__()

    def update_email_schedule(self):
        """
        This API is for Creating Email Schedule
        ---
        tags:
          - Email
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
          - name: query
            in: body
            description: Email Schedule
            required: true
            schema:
              id: Email Schedule
              properties:
                mail_enable:
                    type: boolean
                schedules:
                    types: array
                    example: ["3:4:0 America/Los_Angeles"]
                vessel_ids:
                    types: array
                    example: []
                emails:
                    types: array
                    example: []
        responses:
          500:
            description: Error
          200:
            description: Permission
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)

        # GET HEADER
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)
        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.update_email_schedules(query_json):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "Email schedule successfully updated!"
        data['status'] = "ok"

        return self.return_data(data)

    def update_email_schedules(self, query_json):
        """Update Email Schedules"""

        # DATE FORMAT
        date_format = '%m/%d/%Y %H:%M:%S %Z'

        # GET CURRENT TIME
        update_on = time.time()

        # GET VALUES
        vessel_ids = query_json['vessel_ids']
        mail_enable = query_json['mail_enable']
        emails = query_json['emails']
        schedules = query_json['schedules']

        for vessel_id in vessel_ids:

            # INIT CONDITION
            conditions = []

            # CONDITION FOR QUERY
            conditions.append({
                "col": "vessel_id",
                "con": "=",
                "val": vessel_id
                })

            self.postgres.delete('email_vessel', conditions)

            # LOOP NEW EMAILS
            for email in emails:

                # INIT NEW VESSEL EMAIL
                temp = {}
                temp['vessel_id'] = vessel_id
                temp['email'] = email
                temp['mail_enable'] = mail_enable
                temp['reporting_enable'] = mail_enable
                temp['update_on'] = update_on
                temp['created_on'] = update_on

                # INSERT NEW VESSEL EMAIL
                email_vessel_id = self.postgres.insert('email_vessel',
                                                       temp,
                                                       'email_vessel_id'
                                                      )

                # LOOP NEW SCHEDULES
                for schedule in schedules:

                    sched = schedule.split()
                    tzone = sched[1]
                    tstamp = sched[0].split(":")

                    # TO DATE FORMAT
                    nsched = datetime(
                        2018, 10, 10,
                        int(tstamp[0]),
                        int(tstamp[1]),
                        int(tstamp[2]),
                        tzinfo=dateutil.tz.gettz(tzone)
                    )

                    # TO UTC TIME ZONE
                    utc_sched = nsched.astimezone(timezone('Etc/UTC'))

                    # GET UTC TIME
                    utc_time = utc_sched.strftime(date_format).split()[1]
                    utc_time = utc_time.split(":")

                    seconds_time = timedelta(
                        hours=int(utc_time[0]),
                        minutes=int(utc_time[1]),
                        seconds=int(utc_time[2])
                    )

                    # INIT NEW MAIL SCHEDULE
                    temp = {}
                    temp['email_vessel_id'] = email_vessel_id
                    temp['schedule'] = schedule
                    temp['utc_time'] = seconds_time.total_seconds()
                    temp['update_on'] = update_on
                    temp['created_on'] = update_on

                    # INSERT NEW MAIL SCHEDULE
                    self.postgres.insert('email_schedule', temp)

        # RETURN
        return 1
