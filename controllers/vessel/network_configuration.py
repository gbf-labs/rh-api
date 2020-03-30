#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=too-many-locals, too-many-statements, too-many-branches, too-few-public-methods
"""Network Configuration"""
import math

from flask import request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.postgresql_queries import PostgreSQL

class NetworkConfiguration(Common):
    """Class for NetworkConfiguration"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for NetworkConfiguration class"""
        self._couch_db = CouchDatabase()
        self.postgresql_query = PostgreSQL()
        self.couch_query = Queries()
        self.epoch_default = 26763
        super(NetworkConfiguration, self).__init__()

    def network_configuration(self):
        """
        This API is for Getting Network Configuration
        ---
        tags:
          - Vessel
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
          - name: date
            in: query
            description: Epoch date
            required: false
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
            description: Vessel Device Info
        """

        data = {}

        # VESSEL ID
        vessel_id = request.args.get('vessel_id')
        epoch_date = request.args.get('date')
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
        sort_type = request.args.get('sort_type')
        sort_column = request.args.get('sort_column')
        filter_column = request.args.get('filter_column')
        filter_value = request.args.get('filter_value')

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

        filter_mod_val = ""
        filter_subcat = ""
        filter_option = ""
        filter_val = ""
        if filter_column and filter_value:

            i = 0
            for filter_col in filter_column.split(","):
                if filter_col == "category":
                    filter_mod_val = filter_value.split(",")[i]
                elif filter_col == "sub_category":
                    filter_subcat = filter_value.split(",")[i]
                elif filter_col == "option":
                    filter_option = filter_value.split(",")[i]
                elif filter_col == "value":
                    filter_val = filter_value.split(",")[i]
                i += 1

        data = {}

        data['data'] = []
        total_page = 0

        if epoch_date:

            values = self.couch_query.get_complete_values(
                vessel_id,
                "NTWCONF",
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
            )

        else:

            values = self.couch_query.get_complete_values(
                vessel_id,
                "NTWCONF",
                flag='one_doc'
            )

        if values:

            all_values = values['value']
            timestamp = values['timestamp']

            temp_datas, options, categories = self.values_wrapper("NTWCONF",
                                                                  all_values,
                                                                  timestamp
                                                                 )
            temp_datas = self.add_device_subcategory(temp_datas)
            temp_datas = self.add_device_category(temp_datas)
            rows = self.value_filter(filter_mod_val, filter_subcat,
                                     filter_option, filter_val, temp_datas)

            if sort_type and sort_column:
                sort_column = sort_column.lower()

                if sort_type.lower() == "desc" and sort_column in ['category', 'sub_category',
                                                                   'option', 'value']:
                    rows = sorted(rows, key=lambda i: i[sort_column], reverse=True)
                if sort_type.lower() == "asc":
                    rows = sorted(rows, key=lambda i: i[sort_column])
        else:

            rows = []
            options = []
            categories = []

        datas = self.limits(rows, limit, page)

        total_count = len(datas)
        total_page = int(math.ceil(int(total_count - 1) / limit))

        final_data = []
        temp_category = ''
        temp_subcat = ''
        for item in datas:

            if temp_category == item['category']:
                item['category'] = ''
            else:
                temp_category = item['category']

            if temp_subcat == item['sub_category']:
                item['sub_category'] = ''
            else:
                temp_subcat = item['sub_category']

            final_data.append(item)

        data['data'] = final_data
        data['total_page'] = total_page
        data['limit'] = int(limit)
        data['page'] = int(page)
        data['total_rows'] = total_count
        data['options'] = options
        data['categories'] = categories
        data['subcategories'] = self.get_device_subcategory(datas)
        data['status'] = 'ok'

        return self.return_data(data)
