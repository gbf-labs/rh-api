# pylint: disable=too-many-locals, too-many-statements, too-many-branches
"""Alarm Conditions"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from controllers.alarm.alarm_conditions.alarm_condition_operator import AlarmConditionOperator

class AlarmConditions(Common):
    """Class for AlarmConditions"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmConditions class"""

        self.postgres = PostgreSQL()
        self.operators = AlarmConditionOperator()
        super(AlarmConditions, self).__init__()

    def alarm_conditions(self):
        """
        This API is for Getting Alarm Conditions
        ---
        tags:
          - Alarm Conditions
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
            required: false
            type: integer
          - name: page
            in: query
            description: Page
            required: false
            type: integer
          - name: sort_type
            in: query
            description: Sort Type
            required: false
            type: strings
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
            description: Filter Value
            required: false
            type: string
        responses:
          500:
            description: Error
          200:
            description: Alarm Conditions
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        page = request.args.get('page')
        limit = request.args.get('limit')
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
        datas = self.get_alarm_conditions()
        max_param = self.get_max_param()

        for dta in datas['rows']:

            operator = self.operators.get_alarm_condition_operator(dta['operator_id'])

            if not operator:
                dta['alarm_operator'] = ''
            else:
                dta['alarm_operator'] = operator['operator']

        if datas:

            rows = self.param_filter(datas['rows'], filter_value, checklist=filter_list)

            if sort_type and sort_column:
                sort_column = sort_column.lower()

                cols = ['comment', 'operator', 'parameters']
                if sort_type.lower() == "desc" and sort_column in cols:
                    rows = sorted(rows, key=lambda i: i[sort_column], reverse=True)

                if sort_type.lower() == "asc":
                    rows = sorted(rows, key=lambda i: i[sort_column])

        else:

            rows = []

        if page and limit:

            datas = self.limits(rows, int(limit), int(page))

        else:

            datas = rows
            page = 1
            total_page = 1
            limit = 0

        total_count = len(rows)

        if limit:
            total_page = int(math.ceil(int(total_count - 1) / int(limit)))

        data = self.common_return(datas, total_page, limit, page, total_count)
        data['max_param'] = max_param
        data['status'] = 'ok'

        return self.return_data(data)

    def get_alarm_conditions(self):
        """Get Alarm Conditions"""

        # DATA
        sql_str = "SELECT *  FROM alarm_condition"

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        return data

    # GET ALARM CONDITION
    def get_alarm_condition(self, alarm_condition_id):
        """Get Alarm Condition"""

        assert alarm_condition_id, "Alarm Condition ID is required."

        # DATA
        alarm_condition = []
        sql_str = "SELECT * FROM alarm_condition"
        sql_str = " WHERE alarm_condition_id={0}".format(alarm_condition_id)
        alarm_condition = self.postgres.query_fetch_one(sql_str)

        data = {}
        data['rows'] = alarm_condition

        return data

    def get_max_param(self):
        """Return Maximum Number of Parameter"""

        sql_str = "SELECT jsonb_array_length(parameters) as length FROM alarm_condition"

        param = self.postgres.query_fetch_all(sql_str)

        if param:

            max_param = max([p['length'] for p in param])
        else:

            max_param = 0

        return max_param
