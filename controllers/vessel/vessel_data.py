#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=no-self-use, too-many-locals, too-many-statements, too-many-branches, bare-except
"""Vessel Data"""
# import ConfigParser

import re
import time
import math
from flask import request
from library.couch_database import CouchDatabase
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.common import Common
from library.aws_s3 import AwsS3

class Vessel(Common):
    """Class for Vessel"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Vessel class"""
        # self._my_db = MySQLDatabase()
        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763
        self.aws3 = AwsS3()
        super(Vessel, self).__init__()

        # # INIT CONFIG
        # self.config = ConfigParser.ConfigParser()
        # # CONFIG FILE
        # self.config.read("config/config.cfg")

    # GET VESSEL FUNCTION
    def get_vessels_data(self):
        """
        This API is for Getting Vessel Information
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
          - name: vessel_ids
            in: query
            description: Vessels IDs
            required: false
            type: string

        responses:
          500:
            description: Error
          200:
            description: Vessel Information
        """

        # INIT DATA
        data = {}

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

        # GET ADMIN ROLE AND SUPER ADMIN ROLE
        sql_str = "SELECT role_id FROM role WHERE role_name in ('admin', 'super admin')"
        l_ids = self.postgres.query_fetch_all(sql_str)
        role_ids = [x['role_id'] for x in l_ids]

        str_ids = ""
        if len(role_ids) == 1:

            str_ids = "(" + str(role_ids[0]) + ")"

        else:

            str_ids = str(tuple(role_ids))

        # CREATE SQL QUERY
        # GET ADMIN ACCOUNT
        sql_str = "SELECT * FROM account_role where account_id='" + str(userid)
        sql_str += "' AND role_id in " + str_ids

        res = self.postgres.query_fetch_one(sql_str)

        # EXTRACT VESSELS ID
        extracted_vessel_ids = request.args.get('vessel_ids')
        vessels = []

        if res:
            if extracted_vessel_ids:

                for vessel_id in extracted_vessel_ids.split(","):
                    res = self.couch_query.get_by_id(vessel_id)
                    if res:
                        ves = {}
                        ves['id'] = res['_id']
                        ves['key'] = res['number']
                        vessels.append(ves)

            else:
                vessels = self.couch_query.get_vessels()
        else:
            vessel_ids = []
            try:
                if not extracted_vessel_ids: # EMPTY
                    vessel_ids = []
                else:
                    vessel_ids = extracted_vessel_ids.split(",")
            except:
                data["alert"] = "Invalid Vessel IDs"
                data['status'] = 'Failed'
                # RETURN ALERT
                return self.return_data(data)

            company_ids = self.get_company_id(userid)
            if not company_ids:
                data["message"] = "User Doesn't belong to any company."
                data['rows'] = []
                data['status'] = 'ok'
                # RETURN ALERT
                return self.return_data(data)

            # ACCOUNT'S AVAILABLE VESSELS
            company_vessel_ids = self.get_company_vessels(company_ids)['rows']

            #FILTER VESSELS TO GET
            vessels_to_get = []
            if not vessel_ids:
                vessels_to_get = company_vessel_ids
            else:
                for vessel_id in vessel_ids:
                    # found_vessel = None
                    for company_vessel in company_vessel_ids:
                        if vessel_id == company_vessel['vessel_id']:
                            vessels_to_get.append(company_vessel)
                            break
                if len(vessels_to_get) != len(vessel_ids):
                    data["alert"] = "Some Vessel are not belong to this user."
                    data['status'] = 'Failed'
                    # RETURN ALERT
                    return self.return_data(data)

            temp_ids = []

            for vessel_id in vessels_to_get:

                if vessel_id['vessel_id'] not in temp_ids:

                    temp_ids.append(vessel_id['vessel_id'])
                    res = self.couch_query.get_by_id(vessel_id['vessel_id'])

                    if res:
                        ves = {}
                        ves['id'] = res['_id']
                        ves['key'] = res['number']
                        vessels.append(ves)

        # CHECK DATABASES
        rows = []
        if vessels:

            vessel_ids = [x['id'] for x in vessels]

            # INIT SQL QUERY
            if len(vessel_ids) == 1:
                sql_str = "SELECT * FROM vessel WHERE state ='1'"
                sql_str += " AND vessel_id IN ('{0}')".format(vessel_ids[0])
            else:
                sql_str = "SELECT * FROM vessel WHERE state ='1'"
                sql_str += " AND vessel_id IN {0}".format(tuple(vessel_ids))

            # FETCH ALL
            vessels_state = self.postgres.query_fetch_all(sql_str)

            to_be_install = [x['vessel_id'] for x in vessels_state]

            # LOOP DATABASES
            for item in vessels:
                row = {}

                # GET VESSEL NAME
                vessel_name = self.get_vessel_name(item['id'])

                # self.vessel_name = vessel_name

                # GET LONGITUDE AND LATITUDE
                long_lat = self.get_long_lat(item['id'])

                if long_lat:
                    # get nearest land from ocean to land google map
                    # GET the nearest landmass
                    # https://stackoverflow.com/questions/41539432/google-maps-reverse-
                    # geocoding-api-returns-nearest-land-address-given-a-latlng-in

                    row['long'] = long_lat['long']
                    row['lat'] = long_lat['lat']
                    row['position_source'] = long_lat['position_source']
                else:
                    row['long'] = 0
                    row['lat'] = 0
                    row['position_source'] = ""

                # GET HEADING
                heading, speed = self.get_heading(item['id'])
                if heading:
                    row['heading'] = float(heading['heading'])
                    row['heading_source'] = heading['heading_source']
                else:
                    row['heading_source'] = ""
                    row['heading'] = 0

                if speed:
                    row['speed'] = float(speed)

                # GET UPDATE STATE

                last_update = self.get_last_update_with_option(item['id'])
                epoch_time = int(time.time())

                update_state = self.check_time_lapse(epoch_time, last_update)

                # SET THE RETURN VALUE
                row['isOpen'] = False
                row['vessel_id'] = item['id']
                row['vessel_number'] = item['key']
                row['vessel_name'] = vessel_name
                row['company'] = self.get_vessel_company(item['id'])
                row['update_state'] = update_state

                # GET IMAGE URL
                row['image_url'] = self.aws3.get_vessel_image(item['id'])

                if item['id'] in to_be_install:
                    row['update_state'] = 'white'

                rows.append(row)

            # SORT VESSELS ALPHABETICALLY
            rows = sorted(rows, key=lambda i: i['vessel_name'].upper())

        # SET RETURN
        data['rows'] = rows
        data['companies'] = self.get_vessels_company()
        data['status'] = 'ok'

        # RETURN
        return self.return_data(data)


    # GET THE VESSEL NAME
    def get_vessel_name(self, vessel_id):
        """Return Vessel Name"""
        values = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )
        if values:
            return values['PARAMETERS']['INFO']['VESSELNAME']
        return ''

    def get_long_lat(self, vessel_id):
        """Return Longitude Latitude"""

        all_devices = self.couch_query.get_all_devices(vessel_id)
        devices = []
        source = 'MODEM'
        if all_devices:

            devices = self.get_device(all_devices, source)
            devices_info = 0

            if devices:

                devices_info = self.device_data(source, devices, vessel_id)

            if not devices_info:
                source = 'VSAT'
                devices = self.get_device(all_devices, source)

                if devices:

                    devices_info = self.device_data(source, devices, vessel_id)

            if not devices_info:
                source = 'IOP'
                devices = self.get_device(all_devices, source)

                if devices:

                    devices_info = self.device_data(source, devices, vessel_id)

            if not devices_info:
                source = 'NMEA'
                devices = self.get_device(all_devices, source)
                if devices:

                    devices_info = self.device_data(source, devices, vessel_id)

            if not devices_info:
                source = 'SATC'
                devices = self.get_device(all_devices, source)
                if devices:

                    devices_info = self.device_data(source, devices, vessel_id)

            if not devices_info:
                source = 'VHF'
                devices = self.get_device(all_devices, source)
                if devices:

                    devices_info = self.device_data(source, devices, vessel_id)

            return devices_info

        return 0

    def get_device(self, devices, pattern):
        """Return Device"""

        data = []
        for device in devices:

            if re.findall(r'' + pattern + r'\d', device['doc']['device']):
                data.append(device['doc'])

        data = sorted(data, key=lambda i: i['device'])

        return data

    def get_heading(self, vessel_id):
        """Return Heading"""

        all_devices = self.couch_query.get_all_devices(vessel_id)

        source = 'VSAT'
        devices = self.get_device(all_devices, source)

        data = {}
        speed = 0

        for device in devices:

            values = self.couch_query.get_complete_values(
                vessel_id,
                device['device']
            )

            if values:

                # GET DEVICE NUMBER
                number = device['device'].split(source)[1]

                # GET DEVICE COMPLETE NAME
                heading_source = self.device_complete_name(source, number)

                # SET RETURN
                data['heading'] = values[device['device']]['General']['Heading']
                data['heading_source'] = heading_source

                # RETURN
                # return [data, 0]

        source = 'NMEA'
        devices = self.get_device(all_devices, source)

        for device in devices:

            values = self.couch_query.get_complete_values(
                vessel_id,
                device['device']
            )

            if values:

                # GET DEVICE NUMBER
                number = device['device'].split(source)[1]

                # GET DEVICE COMPLETE NAME
                heading_source = self.device_complete_name(source, number)
                gen = values[device['device']].keys()
                if 'GP0001' in gen:


                    gp0001 = values[device['device']]['GP0001']
                    # SET RETURN

                    if not data:

                        data['heading'] = gp0001['VTG']['courseOverGroundTrueDegrees']
                        data['heading_source'] = heading_source

                    speed = gp0001['VTG']['speedOverGroundKnots']
                    # RETURN
        return [data, speed]

    def get_last_update_with_option(self, vessel_id):
        """Return Last Update with option"""

        values = self.couch_query.get_complete_values(
            vessel_id,
            "COREVALUES",
            flag='one_doc'
        )

        if values:
            return values['timestamp']
        return ''

    def get_company_id(self, userid):
        """Return Company ID"""

        sql_str = "select company_id from account_company where account_id = {}".format(userid)

        res = self.postgres.query_fetch_all(sql_str)

        return res if res else 0

    # GET VESSELS OF COMPANY
    def get_company_vessels(self, company_ids):
        """Return Company Vessels"""

        assert company_ids, "CompanyID is required."

        # DATA
        vessels = []
        for company_id in company_ids:
            sql_str = "SELECT * FROM company_vessels"
            sql_str += " WHERE company_id={0}".format(company_id['company_id'])
            res = self.postgres.query_fetch_all(sql_str)
            if res:
                vessels = vessels + res

        data = {}
        data['rows'] = vessels

        return data

    def device_data(self, source, devices, vessel_id):
        """Return Device Data"""

        for device in devices:

            values = self.couch_query.get_complete_values(
                vessel_id,
                device['device']
            )

            if values:
                try:
                    # GET DEVICE NUMBER
                    number = device['device'].split(source)[1]

                    # GET DEVICE COMPLETE NAME
                    position_source = self.device_complete_name(source, number)

                    # SET RETURN
                    data = {}

                    if source == 'NMEA':
                        lnp = values[device['device']]['GP0001']['GGA']['eastWest']
                        ltp = values[device['device']]['GP0001']['GGA']['northSouth']

                        ln1 = values[device['device']]['GP0001']['GGA']['longitude']
                        lt1 = values[device['device']]['GP0001']['GGA']['latitude']
                        longitude = float(ln1)
                        lat = float(lt1)

                        lat /= 100.
                        dec_lat, degrees_lat = math.modf(lat)
                        dec_lat *= 100.
                        dev_lat = degrees_lat + dec_lat/60

                        longitude /= 100.
                        dec_long, degrees_long = math.modf(longitude)
                        dec_long *= 100.
                        dev_long = degrees_long + dec_long/60

                        data['lat'] = "%.4f" % float(dev_lat)
                        data['long'] = "%.4f" % float(dev_long)

                        if ltp == 'S':

                            data['lat'] = "-" + str(data['lat'])

                        if lnp == 'W':

                            data['long'] = "-" + str(data['long'])

                    elif source == 'SATC':

                        lat_dir = values[device['device']]['General']['latitudeDirection']
                        lon_dir = values[device['device']]['General']['longitudeDirection']

                        lat = values[device['device']]['General']['latitude']
                        lon = values[device['device']]['General']['longitude']

                        lon_val = ''.join(lon.rsplit('.', 1))

                        if lon_dir == 'W':

                            lon_val = "-" + lon_val

                        lat_val = ''.join(lat.rsplit('.', 1))

                        if lat_dir == 'S':

                            lat_val = "-" + lat_val

                        data['long'] = lon_val
                        data['lat'] = lat_val

                    elif source == 'VHF':

                        lat = values[device['device']]['General']['latitude']
                        lon = values[device['device']]['General']['longitude']

                        lon_val = str(lon[1:])
                        lon_val = lon_val.replace('.', '')
                        lon_val = lon_val.replace(',', '.')

                        if lon[0] == 'W':

                            lon_val = "-" + lon_val

                        lat_val = str(lat[1:])
                        lat_val = lat_val.replace('.', '')
                        lat_val = lat_val.replace(',', '.')

                        if lat[0] == 'S':

                            lat_val = "-" + lat_val

                        data['long'] = lon_val
                        data['lat'] = lat_val

                    else:

                        data['long'] = values[device['device']]['General']['Longitude']
                        data['lat'] = values[device['device']]['General']['Latitude']

                    data['position_source'] = position_source

                    # RETURN
                    return data

                except:

                    continue

        return 0

    def get_vessel_company(self, vessel_id):
        """Return Company by Vessel ID"""

        assert vessel_id, "Vessel ID is required."

        data = []
        sql_str = "SELECT * FROM company_vessels cv"
        sql_str += " LEFT JOIN company c ON cv.company_id = c.company_id"
        sql_str += " WHERE vessel_id='{0}'".format(vessel_id)
        result = self.postgres.query_fetch_all(sql_str)

        if result:
            for res in result:
                data.append({
                    'company_id' : res['company_id'],
                    'company_name' : res['company_name']
                })

        return data

    def get_vessels_company(self):
        """ Return Vessel List by Company """

        sql_str = "SELECT v.vessel_id, v.vessel_name, cv.company_id, c.company_name FROM vessel v"
        sql_str += " LEFT JOIN company_vessels cv ON v.vessel_id=cv.vessel_id"
        sql_str += " LEFT JOIN company c ON cv.company_id = c.company_id"
        sql_str += " GROUP BY v.vessel_id, cv.company_id,c.company_id"
        sql_str += " ORDER BY c.company_name"
        results = self.postgres.query_fetch_all(sql_str)

        data = {}
        if results:
            for result in results:
                if result['company_name'] is None:
                    company = "Others"
                else:
                    company = result['company_name']

                formatted = [{
                    'vessel_id' : result['vessel_id'],
                    'vessel_name' : result['vessel_name']
                }]

                if company in data:
                    data[company].append(formatted)
                else:
                    data[company] = formatted

        return data
