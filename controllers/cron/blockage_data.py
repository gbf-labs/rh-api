# pylint: disable=no-self-use, too-many-locals, too-many-statements, bare-except, too-many-branches, too-many-arguments
"""Blockage Data"""
import time
import json
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries
from library.blockages import Blockages

class BlockageData(Common):
    """Class for BlockageData"""

    def __init__(self):
        """The Constructor for BlockageData class"""
        self.blocks = Blockages()
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        self.epoch_default = 26763
        super(BlockageData, self).__init__()

    def run(self):
        """Run Blockage Data"""
        current_date = self.epoch_day(time.time())

        epoch_time = self.days_update(current_date)
        epoch_time -= 1

        datas = self.get_device_type()

        for data in datas:
            self.add_blockage_data(data['vessel_id'], data['device_id'],
                                   data['device'], data['device_type'], epoch_time)


    def get_device_type(self):
        """ Return Device Type  """
        sql_str = "SELECT DISTINCT vessel_id, device_id, device, device_type"
        sql_str += " FROM device WHERE device_type IN"
        sql_str += " ('Intellian_V100_E2S', 'Intellian_V110_E2S',"
        sql_str += " 'Intellian_V80_IARM', 'Intellian_V100_IARM',"
        sql_str += " 'Intellian_V100', 'Intellian_V80_E2S',"
        sql_str += " 'Sailor_900', 'Cobham_500')"
        # sql_str += " AND vessel_id IN ('be942b8ee9e97f4962258c727c0006bd')"
        device_type = self.postgres.query_fetch_all(sql_str)

        return device_type


    def get_device_data(self, vessel_id, device, start, end):
        """ Return Device Data """

        values = self.couch_query.get_complete_values(
            vessel_id,
            device,
            start=str(start),
            end=str(end),
            flag='all')

        if values:
            return values

        return 0

    def  add_blockage_data(self, vessel_id, device_id, device, dtype, epoch_time):
        """ Insert to Blockage Data """

        sql_str = "SELECT epoch_date FROM blockage_data WHERE "
        sql_str += "vessel_id='{0}' AND ".format(vessel_id)
        sql_str += "device_id='{0}' ".format(device_id)
        sql_str += "ORDER BY epoch_date DESC LIMIT 1"
        epoch_date = self.postgres.query_fetch_one(sql_str)

        timestamp = 0
        if epoch_date:
            timestamp = epoch_date['epoch_date']
        else:
            self.log.low("NEW BLOCKAGE DATA!")
            values = self.couch_query.get_complete_values(
                vessel_id,
                device,
                start=str(9999999999),
                end=str(self.epoch_default),
                flag='one_doc',
                descending=False
            )
            timestamp = values['timestamp']

        late_et = self.days_update(timestamp, 1, True)
        late_st = self.days_update(late_et, 1)

        new_et = late_et

        while int(new_et) <= int(epoch_time):

            late_et = self.days_update(late_et, 1, True)
            late_st = self.days_update(late_et, 1)

            if late_st > epoch_time:

                break

            new_et = late_et - 1
            datas = self.get_device_data(vessel_id, device, late_st, late_et)

            try:

                blockage = self.blocks.get_blockage_data(device, datas)
                block_zone = self.blocks.get_blockage_zones(device, dtype, datas)

                # GET ANTENNA STATUS
                antenna = set(data['antenna_status'] for data in blockage)
                coordinates = self.blocks.get_xydata(blockage, antenna, 0, 0, remarks='cron')
                antenna_status = ["{}".format(tmp.capitalize()) for tmp in antenna]

                # INSERT TO BLOCKAGE DATA
                data = {}
                data["vessel_id"] = vessel_id
                data["device_id"] = device_id
                data["antenna_status"] = json.dumps(antenna_status)
                data["coordinates"] = json.dumps(coordinates)
                data["blockzones"] = json.dumps(block_zone)
                data["epoch_date"] = int(late_st)
                data["created_on"] = time.time()
                data["update_on"] = time.time()

                self.postgres.insert('blockage_data', data)
                # self.log.medium("datas: {0}".format(data))

                late_et += 1

            except:
                pass
                # print("Start Time: {0} End Time: {1} No Data Found ".format(late_st, late_et))

        return 1

    def get_blockzones(self, data, zone_number):
        """ Return Block Zones """

        assert data, "Data is required."

        blockzone = []
        blocks = {}
        if zone_number:
            try:
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

                    if bzstatus in data['General']:
                        bz_val = data['General'][bzstatus]

                    if az_start in data['General']:
                        az_start_val = data['General'][az_start]

                    if el_start in data['General']:
                        el_start_val = data['General'][el_start]

                    if az_end in data['General']:
                        az_end_val = data['General'][az_end]

                    if el_end in data['General']:
                        el_end_val = data['General'][el_end]

                    if bz_type in data['General']:
                        bz_type_val = data['General'][bz_type]

                    if blockzones.lower() in data:
                        if not bz_val:
                            bz_val = data[blockzones.lower()]['Status']
                        if not az_start_val:
                            az_start_val = data[blockzones.lower()]['AzStart']
                        if not el_start_val:
                            az_end_val = data[blockzones.lower()]['AzEnd']
                        if not el_end_val:
                            el_end_val = data[blockzones.lower()]['ElEnd']

                    bz_item = {bzstatus: bz_val,
                               az_start: az_start_val,
                               az_end: az_end_val,
                               el_start: el_start_val,
                               el_end: el_end_val,
                               bz_type: bz_type_val}

                    blocks[blockzones] = bz_item

                blockzone.append({"blockage": blocks})

            except ValueError:
                print("No Timestamp found")
        return blockzone
