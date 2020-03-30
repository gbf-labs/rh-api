# pylint: disable=too-many-locals, too-many-branches
"""Alarm Values"""
import math
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries

class AlarmValues(Common):
    """Class for AlarmValues"""

    def __str__(self):
        """ test """

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmValues class"""

        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(AlarmValues, self).__init__()

    def alarm_values(self):
        """
        This API is for Getting Alarm Value
        ---
        tags:
          - Alarm Values
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
            description: Filter Value
            required: false
            type: string
        responses:
          500:
            description: Error
          200:
            description: Alarm Value
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
            data["alert"] = "Invalid Token"
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
        datas = self.get_alarm_values()

        for dta in datas['rows']:
            vessels = dta['vessel']
            vessel_number = self.get_alarm_vessel_name(vessels)

            if not vessel_number:
                dta['vessel_name'] = ''
            else:
                dta['vessel_name'] = ", ".join(vessel_number)
        if datas:

            rows = self.param_filter(datas['rows'], filter_value, checklist=filter_list)

            if sort_type and sort_column:
                sort_column = sort_column.lower()
                if sort_type.lower() == "desc" and sort_column in ['name',
                                                                   'vessel',
                                                                   'device',
                                                                   'device_type',
                                                                   'module',
                                                                   'option',
                                                                   'value']:
                    rows = sorted(rows, key=lambda i: i[sort_column], reverse=True)

                if sort_type.lower() == "asc":
                    rows = sorted(rows, key=lambda i: i[sort_column])
        else:
            rows = []

        datas = self.limits(rows, limit, page)

        #datas = self.get_alarm_vessel_name(datas)

        total_count = len(rows)
        total_page = int(math.ceil(int(total_count - 1) / limit))
        data = self.common_return(datas, total_page, limit, page, total_count)
        data['status'] = 'ok'

        return self.return_data(data)


    def get_alarm_values(self):
        """Return Alarm Values"""

        # DATA
        sql_str = "SELECT * FROM alarm_value"

        datas = self.postgres.query_fetch_all(sql_str)

        data = {}
        data['rows'] = datas

        return data


    # GET ALARM VALUE
    def get_alarm_value(self, alarm_value_id):
        """Return Alarm Value"""

        assert alarm_value_id, "Alarm Value ID is required."

        # DATA
        alarm_value = []
        sql_str = "SELECT * FROM alarm_value WHERE alarm_value_id={0}".format(alarm_value_id)
        alarm_value = self.postgres.query_fetch_one(sql_str)

        data = {}
        data['rows'] = alarm_value

        return data


    def get_alarm_vessel_name(self, vessels):
        """Return Alarm Vessel Name"""

        vessel_number = []

        if vessels:
            for vessel in vessels.split(","):

                values = self.couch_query.get_complete_values(
                    vessel,
                    "PARAMETERS")

                if values:
                    vessel_name = values['PARAMETERS']['INFO']['VESSELNAME']

                else:
                    vessel_name = "Vessel Not Found"

                vessel_number.append(vessel_name)
            return vessel_number

        return 0
