#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=no-self-use, too-many-locals, too-many-arguments, too-many-branches, too-many-statements, too-many-lines, too-many-public-methods, too-many-instance-attributes
"""Device State"""
import math
import re

from configparser import ConfigParser
from flask import request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.unit_conversion import UnitConversion
from library.postgresql_queries import PostgreSQL
from library.config_parser import config_section_parser
from library.aws_s3 import AwsS3

class DeviceState(Common):
    """Class for DeviceState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for DeviceState class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self.postgresql_query = PostgreSQL()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.aws3 = AwsS3()
        self.epoch_default = 26763
        self.db_host = config_section_parser(self.config, "COUCHDB")['host']
        self.db_port = config_section_parser(self.config, "COUCHDB")['port']
        super(DeviceState, self).__init__()

    def device_state(self):

        """
        This API is for Getting Vessel Device Information
        ---
        tags:
          - Devices
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
          - name: device_id
            in: query
            description: Device ID
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
        device_id = request.args.get('device_id')
        epoch_date = request.args.get('date')
        limit = int(request.args.get('limit'))
        page = int(request.args.get('page'))
        sort_type = request.args.get('sort_type')
        sort_column = request.args.get('sort_column')
        filter_column = request.args.get('filter_column')
        filter_value = request.args.get('filter_value')

        # dbs = []
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

        if not device_id or not vessel_id:
            data["alert"] = "Please complete parameters!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)
        if epoch_date in ["null", "0", "NaN", None]:
            epoch_date = False

        device = self.couch_query.get_by_id(device_id)

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        device_type = parameters['PARAMETERS'][device['device']]['TYPE']

        data = {}

        data['data'] = []
        total_page = 0
        total_count = 0

        convert = UnitConversion()
        limit_data = []
        data_id = ""
        if device_type in ['Catalyst_2960', 'Catalyst_3750']:
            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_switch(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Cisco_SNMP']:


            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_cisco_snmp(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Sentry3', 'Raritan_PX2']:

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_pwr_switch(
                vessel_id,
                device['device'],
                end_date=epoch_date,
                dtype=device_type
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])

            if history:

                history = convert.check_unit(gen_datas + history)
                history = self.add_device_subcategory(history)
                history = self.filter_cols(history, filter_column, filter_value)

                if sort_type and sort_column:
                    if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                       'option', 'value']:
                        history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                    elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                        'option', 'value']:
                        history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if item['option'].upper() == 'PDUINLETCURRENT':
                    item['value'] = float(item['value']) / 10

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type == 'IOP':

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_iop(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Intellian_V80_E2S', 'Intellian_V100_E2S',
                             'Intellian_V110_E2S', 'Intellian_V80_IARM',
                             'Intellian_V100_IARM', 'Intellian_V110_IARM',
                             'Intellian_V100', 'Intellian_V110', 'Sailor_900']:

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_vsat(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'

            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)

            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Evolution_X5', 'Evolution_X7']:

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_modem(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['ININMEA']:
            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_inimea(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Danalec_VRI1']:

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_vdr(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Sailor_6103']:

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_alarmpanel(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Sailor_3027C', 'Sailor_62xx']:

            gen_datas, history, modules, options, last_update, data_id = self.get_sailors(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(history, key=lambda i: i[sort])

            if device_type == 'Sailor_62xx':
                for opt in history:

                    if opt['option'] == 'longitude':

                        lon = opt['value']

                        lon_val = str(lon[1:])
                        lon_val = lon_val.replace('.', '')
                        lon_val = lon_val.replace(',', '.')
                        opt['value'] = lon_val

                        if lon[0] == 'W':

                            opt['value'] = "-" + lon_val

                    elif opt['option'] == 'latitude':

                        lat = opt['value']

                        lat_val = str(lat[1:])
                        lat_val = lat_val.replace('.', '')
                        lat_val = lat_val.replace(',', '.')
                        opt['value'] = lat_val

                        if lat[0] == 'S':

                            opt['value'] = "-" + lat_val

            if device_type == 'Sailor_3027C':

                lat_dir = gen_datas[device['device']]['General']['latitudeDirection']
                lon_dir = gen_datas[device['device']]['General']['longitudeDirection']

                for opt in history:

                    if opt['option'] == 'longitude':

                        lon = opt['value']

                        lon_val = str(lon[1:])
                        lon_val = lon_val.replace('.', '')
                        lon_val = lon_val.replace(',', '.')
                        opt['value'] = lon_val

                        if lon_dir == 'W':

                            opt['value'] = "-" + lon_val

                    elif opt['option'] == 'latitude':

                        lat = opt['value']

                        lat_val = str(lat[1:])
                        lat_val = lat_val.replace('.', '')
                        lat_val = lat_val.replace(',', '.')
                        opt['value'] = lat_val

                        if lat_dir == 'S':

                            opt['value'] = "-" + lat_val

            history = convert.check_unit(history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        elif device_type in ['Cobham_500']:

            temp_datas, gen_datas, modules, options, last_update, data_id = self.get_cobham(
                vessel_id,
                device['device'],
                end_date=epoch_date
            )

            data['options'] = options
            data['modules'] = modules
            data['categories'] = modules

            sort = 'module'
            history = sorted(temp_datas, key=lambda i: i[sort])
            history = convert.check_unit(gen_datas + history)
            history = self.add_device_subcategory(history)
            history = self.filter_cols(history, filter_column, filter_value)

            if sort_type and sort_column:
                if sort_type.lower() == "desc" and sort_column in ['module', 'category',
                                                                   'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column], reverse=True)
                elif sort_type.lower() == "asc" and sort_column in ['module', 'category',
                                                                    'option', 'value']:
                    history = sorted(history, key=lambda i: i[sort_column])

            total_count = len(history)
            total_page = int(math.ceil(int(total_count) / limit)) + 1

            limit_data = self.get_limits(history, limit, page)
            final_data = []
            temp_module = ''
            temp_cat = ''
            temp_subcat = ''
            for item in limit_data:

                if temp_module == item['module']:
                    item['module'] = ''
                else:
                    temp_module = item['module']

                if temp_cat == item['category']:
                    item['category'] = ''
                else:
                    temp_cat = item['category']

                if temp_subcat == item['sub_category']:
                    item['sub_category'] = ''
                else:
                    temp_subcat = item['sub_category']

                final_data.append(item)

            data['data'] = final_data
            data['update_state'] = last_update

        else:

            print("device_type: ", device_type)
            print("device_type: ", device_type)
            print("device_type: ", device_type)

        data_url = str(self.db_host) + ":" + str(self.db_port)
        data_url += "/_utils/#database/vessels_db/" + str(data_id)
        data['subcategories'] = self.get_device_subcategory(limit_data)
        data['image_url'] = self.aws3.get_device_image(vessel_id, device_id)
        data['total_page'] = total_page
        data['limit'] = int(limit)
        data['page'] = int(page)
        data['total_rows'] = total_count
        data['status'] = 'ok'
        data['data_url'] = data_url

        return self.return_data(data)

    def get_datas(self, vessel_id, device, end_date=None):
        """Return Datas"""

        if end_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(end_date),
                flag='one_doc'
            )

        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
            )

        return data

    def set_values(self, keys, module, timestamp, value, def_options, device):
        """Set Values"""

        modules = []
        dev_interface = []

        for i in range(1, (len(keys))):
            port = module + str(i)
            if port in keys:

                modules.append({
                    "label": port,
                    "value": port
                    })

                for opt in def_options:

                    interface = {}
                    interface['module'] = port
                    interface['category'] = port
                    interface['option'] = opt
                    interface['value'] = value[device][port][opt]
                    interface['timestamp'] = timestamp

                    dev_interface.append(interface)

        return [dev_interface, modules]

    def set_general(self, device, generals, value, timestamp):
        """Set General"""
        gen_interface = []
        for gen in generals:
            interface = {}
            interface['module'] = 'General'
            interface['category'] = 'General'
            interface['option'] = gen
            interface['value'] = value[device]['General'][gen]
            interface['timestamp'] = timestamp

            gen_interface.append(interface)

        return gen_interface

    def get_switch(self, vessel_id, device, end_date=None):
        """Return Switch"""

        def_options = ['duplex', 'name', 'speed', 'vlan', 'type', 'status']

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        keys = value[device].keys()
        timestamp = data['timestamp']
        data_id = data['_id']

        res_interface, res_modules = self.set_values(keys, 'Fa0/', timestamp, value,
                                                     def_options, device)
        dev_interface += res_interface
        modules += res_modules

        res_interface, res_modules = self.set_values(keys, 'Gi0/', timestamp, value,
                                                     def_options, device)
        dev_interface += res_interface
        modules += res_modules

        # General
        generals = ['SerialNumber', 'MacAddress', 'ModelNumber']
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        complete_option = def_options + generals
        options = self.option_label(complete_option)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_cisco_snmp(self, vessel_id, device, end_date=None):
        """Return Cisco Switch"""

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        timestamp = data['timestamp']
        data_id = data['_id']
        # General
        generals = value[device]['General'].keys()
        cs_datas = self.set_general(device, generals, value, timestamp)

        # Other
        del value[device]['General']

        for key in value[device].keys():

            modules.append({
                "label": key,
                "value": key
                })

            for opt in value[device][key].keys():

                other = {}
                other['module'] = key
                other['category'] = key
                other['option'] = opt
                other['value'] = value[device][key][opt]
                other['timestamp'] = timestamp

                cs_datas.append(other)

        modules = sorted(modules, key=lambda i: i['label'])

        # OPTIONS
        options = [cdata['option'] for cdata in cs_datas]
        options = self.option_label(options)

        return [dev_interface, cs_datas, modules, options, timestamp, data_id]

    def get_pwr_switch(self, vessel_id, device, end_date=None, dtype='Sentry3'):
        """Return Power Switch"""

        def_options = []

        if dtype == 'Sentry3':

            def_options = ['status', 'name', 'ID', 'controlState']

        elif dtype == 'Raritan_PX2':

            def_options = ['status', 'name', 'uptime']

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        keys = value[device].keys()
        timestamp = data['timestamp']
        data_id = data['_id']

        res_interface, res_modules = self.set_values(keys, 'outlet', timestamp, value,
                                                     def_options, device)
        dev_interface += res_interface
        modules += res_modules

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        complete_option = def_options + list(generals)
        options = self.option_label(complete_option)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_iop(self, vessel_id, device, end_date=None):
        """Return IOP"""

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        timestamp = data['timestamp']
        data_id = data['_id']

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        options = self.option_label(generals)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_sailors(self, vessel_id, device, end_date=None):
        """Return IOP"""

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        timestamp = data['timestamp']
        data_id = data['_id']

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        options = self.option_label(generals)

        return [value, gen_interface, modules, options, timestamp, data_id]

    def get_vsat(self, vessel_id, device, end_date=None):
        """Return VSAT"""

        def_options = ['Status', 'AzStart', 'AzEnd', 'ElEnd']

        modules = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        keys = value[device].keys()
        timestamp = data['timestamp']
        data_id = data['_id']

        res_interface, res_modules = self.set_values(keys, 'blockzone', timestamp, value,
                                                     def_options, device)
        dev_interface += res_interface
        modules += res_modules

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        complete_option = def_options + list(generals)
        options = self.option_label(complete_option)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_cobham(self, vessel_id, device, end_date=None):
        """Return Modem"""

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        timestamp = data['timestamp']
        data_id = data['_id']

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        options = self.option_label(generals)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_modem(self, vessel_id, device, end_date=None):
        """Return Modem"""

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        timestamp = data['timestamp']
        data_id = data['_id']

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # OPTIONS
        options = self.option_label(generals)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_inimea(self, vessel_id, device, end_date=None):
        """Return ININMEA"""

        modules = []
        options = []
        temp_options = []

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        timestamp = data['timestamp']
        data_id = data['_id']
        gen_interface = []

        for gen in value[device].keys():

            modules.append({
                'label': gen,
                'value': gen
            })

            gp_s = value[device][gen].keys()
            for gp1 in gp_s:

                opts = value[device][gen][gp1].keys()

                for opt in opts:

                    interface = {}
                    interface['module'] = gen
                    interface['category'] = gp1
                    interface['option'] = opt

                    if opt == 'longitude':

                        lnp = value[device][gen][gp1]['eastWest']
                        longitude = float(value[device][gen][gp1][opt])

                        longitude /= 100.
                        dec_long, degrees_long = math.modf(longitude)
                        dec_long *= 100.
                        dev_long = degrees_long + dec_long/60

                        interface['value'] = dev_long

                        if lnp == 'W':

                            interface['value'] = "-" + str(interface['value'])

                    elif opt == 'latitude':

                        ltp = value[device][gen][gp1]['northSouth']
                        lat = float(value[device][gen][gp1][opt])

                        lat /= 100.
                        dec_lat, degrees_lat = math.modf(lat)
                        dec_lat *= 100.
                        dev_lat = degrees_lat + dec_lat/60

                        interface['value'] = dev_lat

                        if ltp == 'S':

                            interface['value'] = "-" + str(interface['value'])

                    else:

                        interface['value'] = value[device][gen][gp1][opt]

                    interface['timestamp'] = timestamp

                    gen_interface.append(interface)

                    temp_options.append(opt)

        # OPTIONS
        options = self.option_label(temp_options)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def get_vdr(self, vessel_id, device, end_date=None):
        """Return VDR"""

        def_options1 = ['VesselName', 'ImoNumber']
        def_options2 = ['OverallInstance', 'CurrentlyActive']

        modules = []
        options = []

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        keys = value[device].keys()
        timestamp = data['timestamp']
        data_id = data['_id']

        for key in keys:

            modules.append({
                "label": key,
                "value": key
                })

            if key == 'VesselInfo':

                for opt in def_options1:

                    interface = {}
                    interface['module'] = key
                    interface['category'] = key
                    interface['option'] = opt
                    interface['value'] = value[device][key][opt]
                    interface['timestamp'] = timestamp

                    dev_interface.append(interface)

            if key == 'AlarmInfo':

                for opt in def_options2:

                    interface = {}
                    interface['module'] = key
                    interface['category'] = key
                    interface['option'] = opt
                    interface['value'] = value[device][key][opt]
                    interface['timestamp'] = timestamp

                    dev_interface.append(interface)

        # OPTIONS
        complete_option = def_options1 + def_options2
        options = self.option_label(complete_option)

        return [dev_interface, [], modules, options, timestamp, data_id]

    def get_alarmpanel(self, vessel_id, device, end_date=None):
        """Return VDR"""

        modules = []
        options = []
        def_mod = {}

        def_mod['label'] = 'General'
        def_mod['value'] = 'General'
        modules.append(def_mod)

        data = self.get_datas(vessel_id, device, end_date)

        value = data['value']
        dev_interface = []
        timestamp = data['timestamp']
        data_id = data['_id']

        # General
        generals = value[device]['General'].keys()
        gen_interface = self.set_general(device, generals, value, timestamp)

        # Other
        del value[device]['General']

        for key in value[device].keys():

            for opt in value[device][key].keys():

                other = {}
                other['module'] = key
                other['category'] = key
                other['option'] = opt
                other['value'] = value[device][key][opt]
                other['timestamp'] = timestamp

                gen_interface.append(other)

        # OPTIONS
        options = self.option_label(generals)

        return [dev_interface, gen_interface, modules, options, timestamp, data_id]

    def option_label(self, options_data):
        """Return Option Label"""

        options = []
        for dopt in options_data:

            options.append({
                "label": dopt,
                "value": dopt
                })

        return options

    def get_limits(self, option_ids, limit, page):
        """Return Limits"""

        skip = int((page - 1) * limit)

        limit = skip + limit

        return option_ids[skip:limit]

    def filter_cols(self, rows, cols, vals):
        """Filter module, option, value columns"""

        datas = []
        if cols and vals:

            for row in rows:

                column = cols.split(",")
                if 'module' in  column:

                    module = vals.split(",")[column.index('module')]
                    if not self.filter_checker(module, row['module']):
                        continue


                if 'option' in  column:

                    option = vals.split(",")[column.index('option')]
                    if not self.filter_checker(option, row['option']):
                        continue

                if 'value' in  column:

                    value = vals.split(",")[column.index('value')]
                    if not self.filter_checker(value, row['value']):
                        continue

                if 'category' in  column:

                    category = vals.split(",")[column.index('category')]
                    if not self.filter_checker(category, row['category']):
                        continue

                if 'sub_category' in  column:

                    sub_category = vals.split(",")[column.index('sub_category')]
                    if not self.filter_checker(sub_category, row['sub_category']):
                        continue

                datas.append(row)
            return datas

        return rows

    def filter_checker(self, pattern, value):
        """Check Filter"""

        if pattern[0] == "*" and pattern[-1] == "*":

            if not re.findall(pattern[1:-1] + '+', value, re.IGNORECASE):

                return 0

        elif pattern[0] == "*":

            if not value.lower().startswith(pattern[1:].lower()):

                return 0

        elif pattern[-1] == "*":

            if not value.lower().startswith(pattern[:-1].lower()):

                return 0

        else:

            if not value == pattern:

                return 0

        return 1

    def get_option_subcategory(self, option):
        """ Return Option Category """

        assert option, "Option is required."

        if option.upper() in ['IP', 'NETMASK', 'MAC', 'VLAN']:
            category = "Network"

        elif option.upper() in ['MMSI', 'IMO']:
            category = "Vessel Info"

        elif option.upper() in ['SERIALNUMBER', 'PRODUCTNAME']:
            category = "Administration"

        elif option.upper() in ['LONGITUDE', 'LONGITUDEDIR', 'LONGITUDEDIRECTION',
                                'LATITUDE', 'LATITUDEDIR', 'LATITUDEDIRECTION']:
            category = "Positioning"

        else:
            category = "Other"

        return category
