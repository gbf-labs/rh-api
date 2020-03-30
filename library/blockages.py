# pylint: disable=too-many-locals, too-many-branches, no-self-use, too-many-arguments
"""Blockages"""
from library.common import Common
from library.couch_queries import Queries
from library.postgresql_queries import PostgreSQL

class Blockages(Common):
    """Class for Blockages Library"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Blockage class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(Blockages, self).__init__()

    def get_device_type(self, vessel_id, device_id):
        """Get Device Type"""

        assert device_id, "Device ID is required."

        # DATA
        sql_str = "SELECT * FROM device "
        sql_str += "WHERE vessel_id='{0}' ".format(vessel_id)
        sql_str += "AND device_id='{0}'".format(device_id)
        device = self.postgres.query_fetch_one(sql_str)

        return device

    def get_blockage_zones(self, device, device_type, data):
        """ Return Blockage Zones """

        # GET NUMBER OF ZONES
        zone_number = self.get_zone_number(device_type)
        dlist = [tmp['timestamp'] for tmp in data]
        dlist.sort()
        timestamp = dlist[-1]

        blockzone = []
        blocks = {}

        if zone_number and dlist:

            try:
                time_index = dlist.index(timestamp)
                az_start_val = None
                el_start_val = None
                az_end_val = None
                el_end_val = None
                bz_type_val = None
                bz_val = None

                for num in range(1, zone_number + 1):

                    bzstatus = "bz{0}Status".format(num)
                    az_start = "bz{0}AzStart".format(num)
                    el_start = "bz{0}ElStart".format(num)
                    az_end = "bz{0}AzEnd".format(num)
                    el_end = "bz{0}ElEnd".format(num)
                    bz_type = "bz{0}Type".format(num)

                    blockzones = "Blockzone{0}".format(num)

                    if bzstatus in data[time_index]['value'][device]['General']:
                        bz_val = data[time_index]['value'][device]['General'][bzstatus]

                    if az_start in data[time_index]['value'][device]['General']:
                        az_start_val = data[time_index]['value'][device]['General'][az_start]

                    if el_start in data[time_index]['value'][device]['General']:
                        el_start_val = data[time_index]['value'][device]['General'][el_start]

                    if az_end in data[time_index]['value'][device]['General']:
                        az_end_val = data[time_index]['value'][device]['General'][az_end]

                    if el_end in data[time_index]['value'][device]['General']:
                        el_end_val = data[time_index]['value'][device]['General'][el_end]

                    if bz_type in data[time_index]['value'][device]['General']:
                        bz_type_val = data[time_index]['value'][device]['General'][bz_type]

                    if blockzones.lower() in data[time_index]['value'][device]:
                        tmp_holder = data[time_index]['value'][device][blockzones.lower()]
                        if not bz_val:
                            bz_val = tmp_holder['Status']
                        if not az_start_val:
                            az_start_val = tmp_holder['AzStart']
                        if not el_start_val:
                            az_end_val = tmp_holder['AzEnd']
                        if not el_end_val:
                            el_end_val = tmp_holder['ElEnd']

                    bz_item = {bzstatus: bz_val,
                               az_start: az_start_val,
                               az_end: az_end_val,
                               el_start: el_start_val,
                               el_end: el_end_val,
                               bz_type: bz_type_val
                              }

                    blocks[blockzones] = bz_item

                blockzone.append(blocks)

            except ValueError:
                print("No Timestamp found")

        return blockzone


    def get_device_data(self, vessel_id, device, start, end):
        """ Return Device Data """

        values = self.couch_query.get_complete_values(
            vessel_id,
            device,
            start,
            end,
            'all')

        if values:
            return values

        return 0

    def get_blockage_data(self, device, values):
        """ Return Blockage Data """
        blockage = []
        if values:

            for val in values:

                blockage.append({
                    "antenna_status": val['value'][device]['General']['AntennaStatus'],
                    "timestamp": val['timestamp'],
                    "azimuth": val['value'][device]['General']['RelativeAz'],
                    "elevation": val['value'][device]['General']['Elevation'],
                    })

            return blockage
        return 0

    def get_current_position(self, vessel_id, device):
        """ Return Current Position """

        data = {}
        values = self.couch_query.get_complete_values(vessel_id, device)
        if values:
            azimuth = None
            elevation = None

            if 'RelativeAz' in values[device]['General']:
                azimuth = values[device]['General']['RelativeAz']

            if 'Elevation' in values[device]['General']:
                elevation = values[device]['General']['Elevation']

            data['az'] = azimuth
            data['el'] = elevation

            return data
        return 0

    def get_mainloop_time(self, vessel):
        """ Return Mainloop Time """

        values = self.couch_query.get_complete_values(vessel, "PARAMETERS")

        if values:
            return values['PARAMETERS']['MAIN_PROGRAM']['MAINLOOPTIME']
        return 0

    def get_xydata(self, vessel_data, antenna_status, start_time, end_time, remarks):
        """ Return XY Data """

        data = {}
        tmp = []
        for status in antenna_status:
            if remarks == 'cron':
                data[status.capitalize()] = self.get_coordinates(vessel_data, status, 1)

            elif remarks == 'merge':

                coordinates = [data['coordinates'] for data in vessel_data]
                data[status.capitalize()] = self.merge_coordinates(coordinates, status,
                                                                   start_time, end_time)

            else:
                data[status.capitalize()] = self.get_coordinates(vessel_data, status, 0)

        tmp.append(data)

        return data

    def get_coordinates(self, vessel_data, status, flag=True):
        """ Return Coordinates """

        tmp = []
        data = {}
        for vdata in vessel_data:

            if  vdata['antenna_status'] == status:
                if flag == 1:
                    tmp.append({"elevation": float(vdata['elevation']),
                                "azimuth": float(vdata['azimuth']),
                                "timestamp": vdata['timestamp']})
                else:
                    tmp.append({"x-axis": round(float(vdata['elevation'])),
                                "y-axis": round(float(vdata['azimuth']))})

        data['coordinates'] = tmp
        # data['count'] = len(tmp)
        return data

    def combine_axis(self, data):
        """ Combine Axis """

        seen = set()
        tmp = []
        for dta in data:
            tup = tuple(dta.items())
            if tup not in seen:
                seen.add(tup)
                tmp.append(dta)
        return tmp


    def merge_coordinates(self, datas, status, start_time, end_time):
        """ Return Merge Coordinates from PostgreSQL data """

        tmp = []
        coords = []
        data = {}

        for dta in datas:

            if status in dta:
                coords += dta[status]['coordinates']

        coordinates = sorted(coords, key=lambda i: i["timestamp"])

        for coord in coordinates:
            if coord['timestamp'] >= float(start_time) and coord['timestamp'] <= float(end_time):

                tmp.append({"x-axis": round(float(coord['elevation'])),
                            "y-axis": round(float(coord['azimuth']))})

        data['coordinates'] = tmp
        return data

    def antenna_status(self, antennas):
        """ Antenna Status """

        assert antennas, "Antenna is required."

        # antenna_state_online = map(lambda data:data.upper(), ['tracking'])
        antenna_state_online = ['TRACKING']
        antenna_state_offline = ['BLOCKING ZONE', 'ACQUIRING SIGNAL',
                                 'SKYSCAN', 'SEARCH1', 'SEARCH2', 'SEARCH3']
        antenna_state_service = ['ANTENNA POST', 'READY', 'INITIALIZE',
                                 'SETUP', 'DIAGNOSTIC']
        antenna_state_invalid = ['ucli:']

        antenna_status = []
        online_state = []
        offline_state = []
        service_state = []
        invalid_state = []

        for antenna in antennas:

            status = antenna.capitalize()

            if antenna.upper() in antenna_state_online:
                online_state.append(status)

            if antenna.upper() in antenna_state_offline:
                offline_state.append(status)

            if antenna.upper() in antenna_state_service:
                service_state.append(status)

            if antenna.upper() in antenna_state_invalid:
                invalid_state.append(status)

        antenna_status.append({
            "Online": online_state,
            "Offline": offline_state,
            "Service": service_state,
            "Invalid": invalid_state
            })

        return antenna_status

    def get_zone_number(self, device_type):
        """ Return Zone Number """

        assert device_type, "Device Type is required"

        vsat = ['Intellian_V100_E2S', 'Intellian_V110_E2S', 'Intellian_V80_IARM',
                'Intellian_V100_IARM', 'Intellian_V100', 'Intellian_V80_E2S']

        zone = 0  # 'Cobham_500'
        if device_type in vsat:
            zone = 5

        if device_type == "Sailor_900":
            zone = 8

        return zone

    # CHECK DEVICE TYPE IF ALLOWED
    def allowed_device_type(self, device_type):
        """ Check Device Type if map available """

        assert device_type, "Device Type is required."

        allowed_device_type = ['Intellian_V100_E2S', 'Intellian_V110_E2S',
                               'Intellian_V80_IARM', 'Intellian_V100_IARM',
                               'Intellian_V100', 'Intellian_V80_E2S',
                               'Sailor_900', 'Cobham_500']

        if device_type in allowed_device_type:
            return 1

        return 0
