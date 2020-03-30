#====================================#
# AUTHOR:      KRISFEN DUCAO         #
#====================================#
# pylint: disable=no-self-use, too-many-locals, too-many-arguments, too-many-branches, too-many-statements, superfluous-parens
"""Device"""
from __future__ import division
import math
import time
from configparser import ConfigParser
from flask import request
from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.config_parser import config_section_parser
from library.aws_s3 import AwsS3

class Device(Common):
    """Class for Device"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Device class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.aws3 = AwsS3()
        self.epoch_default = 26763
        self.db_host = config_section_parser(self.config, "COUCHDB")['host']
        self.db_port = config_section_parser(self.config, "COUCHDB")['port']
        super(Device, self).__init__()

    # GET VESSEL FUNCTION
    def device_list(self):
        """
        This API is for Getting Vessel Device List
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
            required: false
            type: string
          - name: date
            in: query
            description: Epoch date
            required: false
            type: string
        responses:
          500:
            description: Error
          200:
            description: Vessel Device List
        """
        # VESSEL ID
        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        epoch_date = request.args.get('date')

        # dbs = []
        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        device_list = []

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data = {}
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not vessel_id:
            data = {}
            data["alert"] = "No Vessel ID"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if device_id:

            value = self.couch_query.get_by_id(device_id)
            device_list.append(value)

        else:

            device_list = self.couch_query.get_device(vessel_id)

        if epoch_date in ["null", "0", "NaN"]:
            epoch_date = False

        # REMOVE DATA
        data_to_remove = ['PARAMETERS', 'COREVALUES', 'FAILOVER', 'NTWCONF']
        device_list = self.remove_data(device_list, data_to_remove)

        device_info = {}

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS"
        )

        final_data = []
        for device in device_list:

            current_time = time.time()
            device_type = parameters['PARAMETERS'][device['device']]['TYPE']
            row = {}
            vsat_antenna = {}
            data_id = ""

            if device_type in ['Catalyst_2960', 'Catalyst_3750']:

                device_port, general, all_data, data_id = self.get_switch(vessel_id,
                                                                          device['device'],
                                                                          epoch_date)

                row['ports'] = device_port
                row['general'] = general
                row['device'] = device['device']
                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

            elif device_type in ['Sentry3', 'Raritan_PX2']:

                outlet_status, all_data, data_id = self.get_power_s(vessel_id,
                                                                    device['device'],
                                                                    epoch_date)

                row['outlet_status'] = outlet_status
                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

                gen_data = all_data['value'][device['device']]['General']

                if device_type == 'Sentry3':
                    infeed_load_value = gen_data['infeedLoadValue']
                    infeed_power = gen_data['infeedPower']

                    row['infeed_load_value'] = str(infeed_load_value) + " A"
                    row['infeed_power'] = str(infeed_power) + " W"

                if device_type == 'Raritan_PX2':
                    pdu_inlet_currentval = ""
                    if gen_data['pduInletCurrent']:
                        pdu_inlet_currentval = float(gen_data['pduInletCurrent']) / 10

                    pdu_inlet_current = pdu_inlet_currentval
                    pdu_inlet_voltage = gen_data['pduInletVoltage']
                    pdu_power = ['pduPower']

                    row['pdu_inlet_current'] = pdu_inlet_current
                    row['pdu_line_frequency'] = 'L1' # pduLineFrequency
                    row['pdu_inlet_voltage'] = pdu_inlet_voltage
                    row['pdu_power'] = pdu_power

                row['device'] = device['device']

            elif device_type == 'IOP':

                iop_info, all_data, data_id = self.get_iop(vessel_id, device['device'], epoch_date)
                row['info'] = iop_info

                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

                row['device'] = device['device']

            elif device_type in ['Intellian_V80_E2S', 'Intellian_V100_E2S',
                                 'Intellian_V110_E2S', 'Intellian_V80_IARM',
                                 'Intellian_V100_IARM', 'Intellian_V110_IARM',
                                 'Intellian_V100', 'Intellian_V110', 'Sailor_900']:

                general, all_data, data_id = self.get_vsat(vessel_id, device['device'], epoch_date)

                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']


                row['device'] = device['device']
                row['general'] = general

                vsat_antenna = self.get_vsat_azimuth(row['general'], device_type)

            elif device_type in ['Evolution_X5', 'Evolution_X7']:

                value, all_data, data_id = self.defaul_data(vessel_id, device['device'])

                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

                row['device'] = device['device']
                row['general'] = value[device['device']]['General']

            elif device_type in ['Cisco_SNMP']:

                device_port, general, all_data, data_id = self.get_cis_snmp(vessel_id,
                                                                            device['device'],
                                                                            epoch_date)

                row['ports'] = device_port
                row['general'] = general
                row['device'] = device['device']
                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

            elif device_type in ['Sailor_3027C']:

                general, all_data, data_id = self.get_sailors_30xxx(vessel_id,
                                                                    device['device'],
                                                                    epoch_date)

                row['general'] = general
                row['device'] = device['device']
                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

            elif device_type in ['Sailor_62xx']:

                general, all_data, data_id = self.get_sailor_62xx(vessel_id,
                                                                  device['device'],
                                                                  epoch_date)

                row['general'] = general
                row['device'] = device['device']
                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

            elif device_type in ['Sailor_6103']:

                general, all_data, data_id = self.get_sailor_6103(vessel_id,
                                                                  device['device'],
                                                                  epoch_date)

                row['general'] = general
                row['device'] = device['device']
                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

            elif device_type in ['Cobham_500']:

                value, all_data, data_id = self.defaul_data(vessel_id, device['device'])

                row['description'] = ""

                if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                    row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

                row['device'] = device['device']
                row['general'] = value[device['device']]['General']

            _, all_data, data_id = self.defaul_data(vessel_id, device['device'])

            row['description'] = ""

            if 'DESCRIPTION' in parameters['PARAMETERS'][device['device']].keys():
                row['description'] = parameters['PARAMETERS'][device['device']]['DESCRIPTION']

            row['device'] = device['device']

            if row:

                data_url = str(self.db_host) + ":" + str(self.db_port)
                data_url += "/_utils/#database/vessels_db/" + str(data_id)

                row['status'] = self.check_time_lapse(current_time, all_data['timestamp'])
                row['device_type'] = device_type
                row['device_id'] = device['_id']
                row['vessel_id'] = vessel_id
                row['vsat_antenna'] = vsat_antenna
                row['data_url'] = data_url
                row['image_url'] = self.aws3.get_device_image(vessel_id, device['_id'])
                final_data.append(row)


        device_info['status'] = 'ok'
        device_info['data'] = final_data

        return self.return_data(device_info)

    def get_iop(self, vessel_id, device, epoch_date):
        """Return IOP"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )

        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']

        iop_info = {}
        iop_info['status'] = value[device]['General']['Status']
        iop_info['signal'] = value[device]['General']['Signal']
        iop_info['gps'] = value[device]['General']['GPS']
        iop_info['data'] = value[device]['General']['Data']
        iop_info['handset1'] = value[device]['General']['Handset1']
        iop_info['handset2'] = value[device]['General']['Handset2']
        iop_info['handset3'] = value[device]['General']['Handset3']

        return [iop_info, data, data_id]

    def get_power_s(self, vessel_id, device, epoch_date):
        """Return Power Switch"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
            )

        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']
        device_outlets = []

        for i in range(1, 9):
            temp_device_outlets = {}
            temp_device_outlets['name'] = 'outlet' + str(i)

            if('outlet' + str(i)) in value[device].keys():
                temp_device_outlets['value'] = value[device]['outlet' + str(i)]['status']
            else:
                temp_device_outlets['value'] = None

            device_outlets.append(temp_device_outlets)

        return [device_outlets, data, data_id]

    def get_sailor_6103(self, vessel_id, device, epoch_date):
        """Return Sailor 6103"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )
        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value'][device]
        data_id = data['_id']
        del value['General']

        gen = {}

        for key in value.keys():


            gen[key] = ""
            if not value[key]['IP'] == "0.0.0.0":

                gen[key] = value[key]['IP']

        return [gen, data, data_id]

    def get_sailors_30xxx(self, vessel_id, device, epoch_date):
        """Return Sailor 3027C"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )
        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']

        lat_dir = value[device]['General']['latitudeDirection']
        lon_dir = value[device]['General']['longitudeDirection']
        lat = value[device]['General']['latitude']
        lon = value[device]['General']['longitude']

        lon_val = ''.join(lon.rsplit('.', 1))

        if lon_dir == 'W':

            lon_val = "-" + lon_val

        lat_val = ''.join(lat.rsplit('.', 1))

        if lat_dir == 'S':

            lat_val = "-" + lat_val

        gen = {}
        gen['currentProtocol'] = value[device]['General']['currentProtocol']
        gen['currentOceanRegion'] = value[device]['General']['currentOceanRegion']
        gen['latitude'] = self.position_converter(lat_val)
        gen['longitude'] = self.position_converter(lon_val)
        gen['latitudeDirection'] = lat_dir
        gen['longitudeDirection'] = lon_dir

        return [gen, data, data_id]

    def position_converter(self, val):
        """ POSITION CONVERTER """

        absolute = abs(float(val))
        degrees = math.floor(absolute)
        minutes_not_truncated = (absolute - degrees) * 60
        minutes = math.floor(minutes_not_truncated)
        seconds = math.floor((minutes_not_truncated - minutes) * 60)

        return str(degrees) + "." + str(minutes) + "." + str(seconds)

    def get_sailor_62xx(self, vessel_id, device, epoch_date):
        """Return Sailor 62xx"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )
        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']

        gen = {}
        gen['currentChDesc'] = value[device]['General']['currentChDesc']
        gen['currentCh'] = value[device]['General']['currentCh']
        gen['transmitMode'] = value[device]['General']['transmitMode']

        return [gen, data, data_id]

    def get_switch(self, vessel_id, device, epoch_date):
        """Return Switch"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )
        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']
        device_port = []
        keys = value[device].keys()
        for i in range(1, (len(keys))):
            temp_device_port = {}
            port = 'Fa0/' + str(i)
            if port in keys:

                temp_device_port['name'] = port
                temp_device_port['value'] = value[device][port]['status']
                device_port.append(temp_device_port)

        for i in range(1, 3):
            temp_device_port = {}
            port = 'Gi0/' + str(i)
            if port in keys:

                temp_device_port['name'] = port
                temp_device_port['value'] = value[device][port]['status']
                device_port.append(temp_device_port)

        gen = {}
        gen['port'] = value[device]['General']['port']
        gen['serial'] = value[device]['General']['SerialNumber']
        gen['mac'] = value[device]['General']['MacAddress']
        gen['model'] = value[device]['General']['ModelNumber']

        return [device_port, gen, data, data_id]

    def get_cis_snmp(self, vessel_id, device, epoch_date):
        """Return Switch"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )
        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']
        device_port = []
        keys = value[device].keys()

        for i in range(1, (len(keys))):
            temp_device_port = {}
            port = 'fa' + str(i)
            if port in keys:

                temp_device_port['name'] = port
                temp_device_port['value'] = value[device][port]['ifOperStatus']
                device_port.append(temp_device_port)

        for i in range(1, (len(keys))):
            temp_device_port = {}
            port = 'gi' + str(i)
            if port in keys:

                temp_device_port['name'] = port
                temp_device_port['value'] = value[device][port]['ifOperStatus']
                device_port.append(temp_device_port)

        gen = {}
        for gen_key in value[device]['General'].keys():

            gen[gen_key] = value[device]['General'][gen_key]

        return [device_port, gen, data, data_id]

    def get_vsat(self, vessel_id, device, epoch_date):
        """Return VSAT"""

        if epoch_date:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                str(self.epoch_default),
                str(epoch_date),
                flag='one_doc'
                )

        else:

            data = self.couch_query.get_complete_values(
                vessel_id,
                device,
                flag='one_doc'
                )

        value = data['value']
        data_id = data['_id']

        return [value[device]['General'], data, data_id]

    def defaul_data(self, vessel_id, device):
        """Return Default Data"""

        data = self.couch_query.get_complete_values(
            vessel_id,
            device,
            flag='one_doc'
            )
        value = data['value']
        data_id = data['_id']

        return [value, data, data_id]

    def get_vsat_azimuth(self, general, device_type):
        """Return VSAT Azimuth and Elevation Value"""

        data = {}
        if device_type in ['Intellian_V80_E2S', 'Intellian_V100_E2S',
                           'Intellian_V110_E2S', 'Intellian_V80_IARM',
                           'Intellian_V100_IARM', 'Intellian_V110_IARM',
                           'Intellian_V100', 'Intellian_V110', 'Sailor_900']:

            azimuth = []
            elev = []

            heading = None
            target_azimuth = None
            relative_az = None
            abosulte_az = None

            if 'Heading' in general:
                heading = general['Heading']

            if 'TargetAzimuth' in general:
                target_azimuth = general['TargetAzimuth']

            if 'RelativeAz' in general:
                relative_az = general['RelativeAz']

            if 'AbsoluteAz'  in general:
                abosulte_az = general['AbsoluteAz']

            azimuth.append({
                "Heading": heading,
                "TargetAzimuth": target_azimuth,
                "RelativeAz": relative_az,
                "AbsoluteAz": abosulte_az
                })

            elevation = None
            target_elevation = None

            if 'Elevation' in general:
                elevation = general['Elevation']

            if 'TargetElevation' in general:
                target_elevation = general['TargetElevation']

            elev.append({
                "Elevation": elevation,
                "TargetElevation": target_elevation
                })

            data['azimuth'] = azimuth
            data['elevation'] = elev

        return data
