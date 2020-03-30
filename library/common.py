# pylint: disable=no-self-use, too-many-arguments, too-many-branches, too-many-public-methods, bare-except, unidiomatic-typecheck, no-member
"""Common"""
import time
import operator
from datetime import datetime, timedelta
import re
import simplejson
import dateutil.relativedelta

from flask import jsonify
from library.postgresql_queries import PostgreSQL
from library.log import Log

class Common():
    """Class for Common"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Common class"""
        self.log = Log()

        # INITIALIZE DATABASE INFO
        self.postgres = PostgreSQL()

    # RETURN DATA
    def return_data(self, data):
        """Return Data"""
        # RETURN
        return jsonify(
            data
        )

    # REMOVE KEY
    def remove_key(self, data, item):
        """Remove Key"""

        # CHECK DATA
        if item in data:

            # REMOVE DATA
            del data[item]

        # RETURN
        return data

    # REMOVE SPECIAL CHARACTER
    def remove_special_char(self, data):
        """Remove Special Character"""
        return data.replace("'", "")

    # # GET INFO
    # def get_info(self, columns, table):
    #     """Return Information"""
    #     # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
    #     if not columns:
    #         return 0

    #     # INITIALIZE
    #     cols = ''
    #     count = 1

    #     # LOOP COLUMNS
    #     for data in columns:

    #         # CHECK IF COUNT EQUAL COLUMN LENGHT
    #         if len(columns) == count:

    #             # ADD DATA
    #             cols += data
    #         else:

    #             # ADD DATA
    #             cols += data + ", "

    #         # INCREASE COUNT
    #         count += 1

    #     # CREATE SQL QUERY
    #     sql_str = "SELECT " + cols + " FROM " + table

    #     # CONNECT TO DATABASE
    #     self.my_db.connection_to_db(self.my_db.database)

    #     # CALL FUNCTION QUERY ONE
    #     ret = self.my_db.query_fetch_one(sql_str)

    #     # CLOSE CONNECTION
    #     self.my_db.close_connection()

    #     # RETURN
    #     return ret

    # # GET INFOS
    # def get_infos(self, columns, table):
    #     """Return Set of Information"""
    #     # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
    #     if not columns:
    #         return 0

    #     # INITIALIZE
    #     cols = ''
    #     count = 1

    #     # LOOP COLUMNS
    #     for data in columns:

    #         # CHECK IF COUNT EQUAL COLUMN LENGHT
    #         if len(columns) == count:

    #             # ADD DATA
    #             cols += data

    #         else:

    #             # ADD DATA
    #             cols += data + ", "

    #         # INCREASE COUNT
    #         count += 1

    #     # CREATE SQL QUERY
    #     sql_str = "SELECT " + cols + " FROM " + table

    #     # INITIALIZE DATABASE INFO
    #     # self.my_db = MySQLDatabase()

    #     # CONNECT TO DATABASE
    #     self.my_db.connection_to_db(self.my_db.database)

    #     # CALL FUNCTION QUERY ONE
    #     ret = self.my_db.query_fetch_all(sql_str)

    #     # CLOSE CONNECTION
    #     self.my_db.close_connection()

    #     # RETURN
    #     return ret

    # GET USER INFO
    def get_user_info(self, columns, table, user_id, token):
        """Return User Information"""
        # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
        if not columns:
            return 0

        # INITIALIZE
        cols = ''
        count = 1

        # LOOP COLUMNS
        for data in columns:

            # CHECK IF COUNT EQUAL COLUMN LENGHT
            if len(columns) == count:

                # ADD DATA
                cols += data

            else:

                # ADD DATA
                cols += data + ", "

            # INCREASE COUNT
            count += 1

        # CREATE SQL QUERY
        sql_str = "SELECT " + cols + " FROM " + table + " WHERE "
        sql_str += " token = '" + token + "'"
        sql_str += " AND id = '" + user_id + "'"
        sql_str += " AND status = true"

        # CALL FUNCTION QUERY ONE
        ret = self.postgres.query_fetch_one(sql_str)

        # RETURN
        return ret

    # VALIDATE TOKEN
    def validate_token(self, token, user_id):
        """Validate Token"""
        # import datetime
        # import dateutil.relativedelta

        # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
        if not token:
            return 0

        # SET COLUMN FOR RETURN
        columns = ['username', 'update_on']

        # CHECK IF TOKEN EXISTS
        user_data = self.get_user_info(columns, "account", user_id, token)

        data = {}
        data['update_on'] = time.time() #datetime.fromtimestamp(time.time())

        condition = []
        temp_con = {}

        temp_con['col'] = 'id'
        temp_con['val'] = user_id
        temp_con['con'] = "="
        condition.append(temp_con)

        self.postgres = PostgreSQL()

        # self.postgres.update('account', data, condition)

        # CHECK IF COLUMN EXIST,RETURN 0 IF NOT
        if user_data:

            dt1 = datetime.fromtimestamp(user_data['update_on'])
            dt2 = datetime.fromtimestamp(time.time())
            dateutil.relativedelta.relativedelta(dt2, dt1)

            rd1 = dateutil.relativedelta.relativedelta(dt2, dt1)
            # print(rd1.years, rd1.months, rd1.days, rd1.hours, rd1.minutes, rd1.seconds)

            if rd1.years or rd1.months or rd1.days or rd1.hours:

                return 0

            if rd1.minutes > 30:

                return 0

        else:

            return 0

        self.postgres.update('account', data, condition)

        # RETURN
        return 1

    def device_complete_name(self, name, number=''):
        """Return Device Complete Name"""
        # SET READABLE DEVICE NAMES
        humanize_array = {}
        humanize_array['NTWCONF'] = 'Network Configuration'
        humanize_array['NTWPERF'] = 'Network Performance ' + str(number)
        humanize_array['COREVALUES'] = 'Core Values'
        humanize_array['IOP'] = 'Irridium OpenPort ' + str(number)
        humanize_array['VDR'] = 'VDR ' + str(number)
        humanize_array['VSAT'] = 'V-SAT ' + str(number)
        humanize_array['MODEM'] = 'MODEM ' + str(number)
        humanize_array['FBB'] = 'FleetBroadBand ' + str(number)
        humanize_array['VHF'] = 'VHF ' + str(number)
        humanize_array['SATC'] = 'SAT-C ' + str(number)
        humanize_array['NMEA'] = 'NMEA ' + str(number)

        # RETURN
        return humanize_array[name]

    # COUNT DATA
    def count_data(self, datas, column, item):
        """Return Data Count"""

        # INITIALIZE
        count = 0

        # LOOP DATAS
        for data in datas:

            # CHECK OF DATA
            if data[column] == item:

                # INCREASE COUNT
                count += 1

        # RETURN
        return count

    # REMOVE KEY
    def remove_data(self, datas, remove):
        """Remove Data"""
        ret_data = []

        # CHECK DATA
        for data in datas:
            if not data['device'] in remove:
                ret_data.append(data)

        # RETURN
        return ret_data

    def set_return(self, datas):
        """Set Return"""
        ret_data = {}
        ret_data['data'] = []
        for data in datas:
            ret_data['data'].append(data['value'])

        return ret_data

    def check_time_lapse(self, current, timestamp):
        """Check Time lapse"""
        # from datetime import datetime
        struct_now = time.localtime(current)

        new_time = time.strftime("%m/%d/%Y %H:%M:%S %Z", struct_now)

        try:
            vessel_time = time.localtime(timestamp)

            vessel_time = time.strftime("%m/%d/%Y %H:%M:%S %Z", vessel_time)

            vessel_time = vessel_time.split(' ')
            v_time = vessel_time[1]
            v_date = vessel_time[0]

            new_time = new_time.split(' ')
            n_time = new_time[1]
            n_date = new_time[0]


            start_date = datetime.strptime(v_date, "%m/%d/%Y")
            end_date = datetime.strptime(n_date, "%m/%d/%Y")

            # if not abs((start_date-start_date).days):
            if not abs((start_date-end_date).days):

                formatted = '%H:%M:%S'
                tdelta = datetime.strptime(str(n_time),
                                           formatted) - datetime.strptime(str(v_time), formatted)

                tdelta = str(tdelta).split(":")

                try:

                    if int(tdelta[0]):
                        return 'red'

                    if int(tdelta[1]) < 15:
                        return 'green'

                    if int(tdelta[1]) < 20:
                        return 'orange'

                except:

                    return 'red'

            return 'red'

        except:

            return 'red'

    def get_ids(self, datas):
        """Return IDs"""
        module_ids = []

        for data in datas or []:

            module_ids.append(data['module'])

        return module_ids

    def check_request_json(self, query_json, important_keys):
        """Check Request Json"""
        query_json = simplejson.loads(simplejson.dumps(query_json))

        for imp_key in important_keys.keys():

            if type(query_json.get(imp_key)):

                if type(query_json[imp_key]) != type(important_keys[imp_key]):

                    return 0

            else:

                return 0

        return 1

    def milli_to_sec(self, millis):
        """Cobert Millisecond to second"""
        try:

            # SET TO INT
            millis = int(millis)

            # CONVERT
            seconds = (millis/1000)

            # RETURN
            return int(seconds)

        except:
            return 0

    def values_wrapper(self, device, datas, timestamp):
        """Values Wrapper"""
        rows = []
        modules = []
        options = []

        opt_list = []
        for module in datas[device]:

            if module != '_ExtractInfo':

                modules.append({
                    "label": module,
                    "value": module
                    })

                for option in datas[device][module]:
                    row = {}

                    if option not in opt_list:

                        options.append({
                            "label": option,
                            "value": option
                        })

                        opt_list.append(option)

                    row['device'] = device
                    row['module'] = module
                    row['option'] = option
                    row['option'] = option
                    row['timestamp'] = timestamp
                    if type(datas[device][module][option]) == str:
                        row['value'] = datas[device][module][option].rstrip("\n\r")
                    else:
                        row['value'] = datas[device][module][option]

                    rows.append(row)

        return [rows, options, modules]

    def limits(self, rows, limit, page):
        """Limits"""
        skip = int((page - 1) * limit)

        limit = skip + limit

        return rows[skip:limit]

    def value_filter(self, filter_mod_val, filter_subcat, filter_option, filter_val, temp_datas):
        """Value Filter"""

        if not filter_mod_val and not filter_option and not filter_val and not filter_subcat:

            return temp_datas

        mod_datas = []

        if filter_mod_val:

            for temp_data in temp_datas:

                if self.filter_checker(str(filter_mod_val), str(temp_data['category'])):
                    mod_datas.append(temp_data)

        else:

            mod_datas = temp_datas

        subcat_datas = []
        if filter_subcat:

            for mod_data in mod_datas:
                if self.filter_checker(str(filter_subcat), str(mod_data['sub_category'])):
                    subcat_datas.append(mod_data)

        else:

            subcat_datas = mod_datas

        opt_datas = []
        if filter_option:

            for subcat_data in subcat_datas:

                if self.filter_checker(str(filter_option), str(subcat_data['option'])):
                    opt_datas.append(subcat_data)

        else:

            opt_datas = subcat_datas

        val_datas = []
        if filter_val:

            for opt_data in opt_datas:

                if self.filter_checker(str(filter_val), str(opt_data['value'])):
                    val_datas.append(opt_data)

        else:

            val_datas = opt_datas

        return val_datas


    def param_filter(self, temp_datas, params, checklist):
        """Parameter Filter"""
        if not params:

            return temp_datas

        param_datas = []
        param_datas = temp_datas

        output = []

        i = 0

        for param in params:
            key = checklist[i]

            i += 1

            for data in param_datas:

                if self.filter_checker(str(param), str(data[key])):

                    output.append(data)

        return output

    def filter_checker(self, pattern, value):
        """Check Filter"""
        if '*' in pattern:
            pattern = pattern.replace('.', r'\.')
            if pattern == "*":
                pattern = "."

            if not pattern[0] == "*" and pattern != ".":
                pattern = "^" + str(pattern)

            if pattern[-1] == "*":
                pattern = pattern[:-1] + '+'

            if not pattern[-1] == "+" and pattern != ".":
                pattern = str(pattern) + '$'

            if pattern[0] == "*":
                pattern = '.?' + pattern[1:]

            pattern = pattern.replace('*', '.+')

            # print("pattern: ", pattern)

            try:

                if not re.findall(pattern, value, re.IGNORECASE):

                    return 0

            except:

                return 0

        else:

            if not value == pattern:

                return 0

        return 1

    def isfloat(self, data):
        """Check if float"""
        try:
            if data == "infinity":
                return False

            float(data)
        except ValueError:
            return False
        else:
            return True

    def isint(self, data):
        """Check if Integer"""
        try:
            if data == "infinity":
                return False

            tmp_data1 = float(data)
            tmp_data2 = int(tmp_data1)
        except ValueError:
            return False
        else:
            return tmp_data1 == tmp_data2

    def compute_operator(self, param1, comparator, param2=None):
        """Compute Operator Result"""

        if type(param1) == str:
            param1 = param1.upper()

        if type(param2) == str:
            param2 = param2.upper()

        if comparator == "LIKE":
            return bool(param1 == param2)

        if comparator == "!LIKE":
            return bool(param1 != param2)

        ops = {'>': operator.gt,
               '<': operator.lt,
               '=': operator.eq,
               '>=': operator.ge,
               '<=': operator.le,
               '!=': operator.ne,
               '~': operator.invert,
               'AND': operator.and_,
               'OR': operator.or_,
               '+': operator.add,
               '-': operator.sub,
               '*': operator.mul,
               '/': operator.truediv
              }

        if param2 is None:

            return ops[comparator](param1)

        return ops[comparator](param1, param2)


    def time_span(self, dt2, dt1):
        """Time Span"""
        # import datetime
        # from datetime import datetime
        # import dateutil.relativedelta

        dt1 = datetime.fromtimestamp(dt1)
        dt2 = datetime.fromtimestamp(dt2)
        rel_delta = dateutil.relativedelta.relativedelta(dt2, dt1)

        years = str(rel_delta.years) + " Year "
        if rel_delta.years > 1:
            years = str(rel_delta.years) + " Years "

        months = str(rel_delta.months) + " Month "
        if rel_delta.months > 1:
            months = str(rel_delta.months) + " Months "

        days = str(rel_delta.days) + " Day "
        if rel_delta.days > 1:
            days = str(rel_delta.days) + " Days "

        hours = str(rel_delta.hours) + " Hour "
        if rel_delta.hours > 1:
            hours = str(rel_delta.hours) + " Hours "

        minutes = str(rel_delta.minutes) + " Minute "
        if rel_delta.minutes > 1:
            minutes = str(rel_delta.minutes) + " Minutes "

        seconds = str(rel_delta.seconds) + " Second"
        if rel_delta.seconds > 1:
            seconds = str(rel_delta.seconds) + " Seconds"

        ret = years + months + days + hours + minutes + seconds

        return ret

    def days_update(self, timestamp, count=0, add=False):
        """Days Update"""
        try:

            named_tuple = time.localtime(int(timestamp))

            # GET YEAR MONTH DAY
            year = int(time.strftime("%Y", named_tuple))
            month = int(time.strftime("%m", named_tuple))
            day = int(time.strftime("%d", named_tuple))

            # Date in tuple
            date_tuple = (year, month, day, 0, 0, 0, 0, 0, 0)

            local_time = time.mktime(date_tuple)
            orig = datetime.fromtimestamp(local_time)

            if add:

                new = orig + timedelta(days=count)

            else:

                new = orig - timedelta(days=count)

            return new.timestamp()

        except:
            return 0

    def epoch_day(self, timestamp):
        """Epoch Day"""
        try:

            named_tuple = time.localtime(int(timestamp))

            # GET YEAR MONTH DAY
            year = int(time.strftime("%Y", named_tuple))
            month = int(time.strftime("%m", named_tuple))
            day = int(time.strftime("%d", named_tuple))

            # Date in tuple
            date_tuple = (year, month, day, 0, 0, 0, 0, 0, 0)

            return time.mktime(date_tuple)

        except:

            return 0


    def timediff_update(self, timestamp, count=0, key=None):
        """Time Difference Update"""
        try:

            named_tuple = time.localtime(int(timestamp))

            # GET YEAR MONTH DAY
            year = int(time.strftime("%Y", named_tuple))
            month = int(time.strftime("%m", named_tuple))
            day = int(time.strftime("%d", named_tuple))
            hour = int(time.strftime("%H", named_tuple))
            minute = int(time.strftime("%M", named_tuple))
            second = int(time.strftime("%S", named_tuple))
            # Date in tuple
            date_tuple = (year, month, day, hour, minute, second, 0, 0, 0)

            local_time = time.mktime(date_tuple)
            orig = datetime.fromtimestamp(local_time)


            if key == "hours":
                new = orig - timedelta(hours=count)

            else:
                new = orig - timedelta(days=count)

            return new.timestamp()

        except:
            return 0

    def datedelta(self, timestamp, days=0, months=0, years=0):
        """Return DateDelta"""
        tme = time.gmtime(timestamp)
        new_time = "{0}-{1}-{2}".format(tme.tm_year, tme.tm_mon, tme.tm_mday)

        date1 = datetime.strptime(new_time, "%Y-%m-%d")
        date2 = date1 - dateutil.relativedelta.relativedelta(days=days, months=months, years=years)
        # self.log.low("d2: {0}".format(d2))

        return date2.timestamp()


    def data_filter(self, datas, key):
        """Filter Data"""
        temp_data = []

        if datas and key:

            key = "{0}s".format(key)

            data_list = []
            for data in datas[key]:

                data_list.append(data)

            for data in data_list:
                if data in [True, False]:
                    data = "{0}".format(data)

                if key == "statuss":

                    if data == "True":
                        data = "Enabled"

                    if data == "False":
                        data = "Disabled"

                temp_data.append({
                    "label": data,
                    "value": data
                    })


        return  temp_data

    def common_return(self, datas, total_page, limit, page, total_rows):
        """Common Return for Data"""
        data = {}
        data['data'] = datas
        data['total_page'] = total_page
        data['limit'] = int(limit)
        data['page'] = int(page)
        data['total_rows'] = total_rows

        return data

    def file_replace(self, filename):
        """ File Naming """

        file_name = filename.split(".")[0]

        if "_" in file_name:

            suffix = file_name.split("_")[-1]

            if suffix.isdigit():
                new_name = filename.replace(suffix, str(int(suffix) + 1))
            else:
                new_name = filename.replace(suffix, str(suffix+"_1"))
        else:
            new_name = filename.replace(file_name, str(file_name+"_1"))

        return new_name

    def get_subcategory_option(self, option):
        """ Return Sub Category for Option """
        assert option, "Option is required."

        # DATA
        sql_str = "SELECT subcategory_name FROM subcategory c "
        sql_str += "LEFT JOIN subcategory_options co ON c.subcategory_id = co.subcategory_id "
        sql_str += "WHERE co.option ILIKE '{0}'".format(option)

        res = self.postgresql_query.query_fetch_one(sql_str)

        if res:
            result = res['subcategory_name']
        else:
            result = "Others"

        return result

    def get_device_subcategory(self, datas):
        """ Return Device Categories """

        categories = []
        if datas:
            cats = set(data['sub_category'] for data in datas)

            for cat in cats:
                if cat != "":
                    categories.append({
                        "label": cat,
                        "value": cat
                    })

        return categories

    def add_device_subcategory(self, datas):
        """ Add Sub Category """
        assert datas, "Data is required."

        options = [data['option'] for data in datas]

        i = 0
        for opt in options:

            try:
                # datas[i]['sub_category'] = self.get_option_subcategory(opt)
                datas[i]['sub_category'] = self.get_subcategory_option(opt)

            except ValueError:
                print("No Index found")
            i += 1
        return datas

    def add_device_category(self, datas):
        """ Add Category based in module """

        assert datas, "Data is required."

        for data in datas:
            data['category'] = data['module']
            del data['module']

        return datas

    def format_filter(self, datas):
        """ Return Filter in Format """

        tmp = []

        for data in datas:

            tmp.append({
                "label": data,
                "value": data
            })

        return tmp
