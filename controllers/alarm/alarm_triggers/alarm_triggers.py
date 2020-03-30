# pylint: disable=too-many-locals, too-many-branches
"""Alarm Triggers"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm.alarm_type import AlarmType

class AlarmTriggers(Common):
    """Class for AlarmTriggers"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmTriggers class"""

        self.postgres = PostgreSQL()
        self.alarm_type = AlarmType()
        super(AlarmTriggers, self).__init__()

    def alarm_triggers(self):
        """
        This API is for Getting Alarm Trigger
        ---
        tags:
          - Alarm Triggers
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
          - name: limit
            in: query
            description: Limit
            required: true
            type: integer
          - name: page
            in: query
            description: Page
            required: true
            type: integer
          - name: sort_type
            in: query
            description: Sort Type
            required: false
            type: string
          - name: sort_column
            in: query
            description: Sort Column
            required: false
            type: string
          - name: filter_column
            in: query
            description: Filter Column
            required: false
            type: string
          - name: filter_value
            in: query
            description: Filter Trigger
            required: false
            type: string
        responses:
          500:
            description: Error
          200:
            description: Alarm Trigger
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        page = int(request.args.get('page'))
        limit = int(request.args.get('limit'))
        sort_type = request.args.get('sort_type')
        sort_column = request.args.get('sort_column')
        filter_column = request.args.get('filter_column')
        filter_value = request.args.get('filter_value')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data['alert'] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if filter_column and filter_value:
            filter_list = []
            for col in filter_column.split(","):
                filter_list.append(col)

            filter_val = []
            for val in filter_value.split(","):
                filter_val.append(val)

            filter_value = tuple(filter_val)

        else:
            filter_list = filter_column

        data['data'] = []
        total_page = 0

        #GET DATA
        datas = self.get_alarm_triggers()

        for dta in datas['rows']:

            alarm_type = self.alarm_type.alarm_type(dta['alarm_type_id'])

            if not alarm_type:
                dta['alarm_type'] = ''
            else:
                dta['alarm_type'] = alarm_type['alarm_type']

        if datas:

            rows = self.param_filter(datas['rows'], filter_value, checklist=filter_list)

            if sort_type and sort_column:
                sort_column = sort_column.lower()

                if sort_type.lower() == "desc" and sort_column in ['alarm_type_id',
                                                                   'alarm_condition_id',
                                                                   'label',
                                                                   'description']:
                    rows = sorted(rows, key=lambda i: i[sort_column], reverse=True)

                if sort_type.lower() == "asc":
                    rows = sorted(rows, key=lambda i: i[sort_column])

        else:
            rows = []

        datas = self.limits(rows, limit, page)

        total_count = len(rows)
        total_page = int(math.ceil(int(total_count - 1) / limit))

        data = self.common_return(datas, total_page, limit, page, total_count)
        data['status'] = 'ok'

        return self.return_data(data)

    def get_alarm_triggers(self):
        """Get Alarm Triggers"""

        # DATA
        sql_str = "SELECT t.*, c.comment as alarm_condition_label FROM alarm_trigger t"
        sql_str += " LEFT JOIN alarm_condition c"
        sql_str += " ON t.alarm_condition_id = c.alarm_condition_id"

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        return data
