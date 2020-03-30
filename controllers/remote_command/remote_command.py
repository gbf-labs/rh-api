# pylint: disable=no-self-use, too-many-locals, too-many-statements, too-many-branches
"""Remote Command"""
import re
from configparser import ConfigParser
from flask import  request

from library.couch_database import CouchDatabase
from library.couch_queries import Queries
from library.common import Common
from library.postgresql_queries import PostgreSQL

class RemoteCommand(Common):
    """Class for RemoteCommand"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for RemoteCommand class"""
        # INIT CONFIG
        self.config = ConfigParser()

        # CONFIG FILE
        self.config.read("config/config.cfg")

        self._couch_db = CouchDatabase()
        self.couch_query = Queries()
        self.postgres = PostgreSQL()
        self.epoch_default = 26763
        super(RemoteCommand, self).__init__()

    # GET VESSEL FUNCTION
    def remote_command(self):
        """
        This API is for Remote Command
        ---
        tags:
          - Remote Command
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

        responses:
          500:
            description: Error
          200:
            description: Remote Command
        """
        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data = {}
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        vessel_id = request.args.get('vessel_id')
        device_id = request.args.get('device_id')
        device_info = {}
        all_devices = self.couch_query.get_all_devices(vessel_id)

        if device_id:

            for dev in all_devices:

                if dev['id'] == device_id:

                    device_info = dev

                    break

        parameters = self.couch_query.get_complete_values(
            vessel_id,
            "PARAMETERS",
            flag='one_doc'
        )

        ntwconf = self.couch_query.get_complete_values(
            vessel_id,
            "NTWCONF",
            flag='one_doc'
        )
        # COREVALUES, FAILOVER, NTWCONF
        final_data = []

        if device_id and not device_info:
            pass

        elif device_id and device_info:

            if device_info['doc']['device'] == "COREVALUES":
                system = self.get_system()
                final_data.append(system)

            if device_info['doc']['device'] == "FAILOVER":
                failover = self.get_failover(parameters)
                final_data.append(failover)

            if device_info['doc']['device'] == "NTWCONF":
                netconf = self.get_nc(parameters, ntwconf)
                final_data.append(netconf)

            devices = self.get_item([device_info], 'MODEM')
            for device in devices:

                modem = self.get_modem(vessel_id, device)
                final_data.append(modem)

            devices = self.get_item([device_info], 'POWERSWITCH')
            for device in devices:

                power = self.get_power_switch(vessel_id, device)
                final_data.append(power)

        else:

            system = self.get_system()
            final_data.append(system)

            failover = self.get_failover(parameters)
            final_data.append(failover)

            netconf = self.get_nc(parameters, ntwconf)
            final_data.append(netconf)

            devices = self.get_item(all_devices, 'MODEM')
            for device in devices:

                modem = self.get_modem(vessel_id, device)
                final_data.append(modem)

            devices = self.get_item(all_devices, 'POWERSWITCH')
            for device in devices:

                power = self.get_power_switch(vessel_id, device)
                final_data.append(power)

        if not device_id:
            tun1 = ''
            if 'tun1' in ntwconf['value']['NTWCONF'].keys():

                tun1 = ntwconf['value']['NTWCONF']['tun1']['IP']

            ssh_opt = []
            opt = {}
            opt['description'] = "SSH to Vessel"
            opt['option'] = "ssh://" + tun1

            ssh_opt.append(opt)

            ssh = {}
            ssh['icon'] = "CodeIcon"
            ssh['label'] = "SSH"
            ssh['options'] = ssh_opt
            final_data.append(ssh)

        ret = {}
        ret['data'] = final_data
        ret['status'] = "ok"

        return self.return_data(ret)

    def get_system(self):
        """ SYSTEM / CORE VALUES """

        system = {}
        system["label"] = "System"
        system["icon"] = "Apps"
        system["options"] = []

        option = {}
        option["option"] = "Load-average"
        option["description"] = 'Gets the number of processor cores and load-average.'
        system["options"].append(option)

        option = {}
        option["option"] = "Uptime"
        option["description"] = 'Get the uptime of the system, aswell as the start-up timestamp.'
        system["options"].append(option)

        option = {}
        option["option"] = "Free RAM and Swap"
        option["description"] = 'Show the available/used RAM and swap size'
        system["options"].append(option)

        option = {}
        option["option"] = "Hardware info"
        option["description"] = 'Show hardware info (like serial-number, product name, ...)'
        system["options"].append(option)

        option = {}
        option["option"] = "Memory info"
        option["description"] = 'Show memory info'
        system["options"].append(option)

        option = {}
        option["option"] = "Disk space"
        option["description"] = 'Check used/available disk space'
        system["options"].append(option)

        option = {}
        option["option"] = "Debian version"
        option["description"] = 'Get debian and kernel version'
        system["options"].append(option)

        option = {}
        option["option"] = "PWD"
        option["description"] = 'Get working directory'
        system["options"].append(option)

        option = {}
        option["option"] = "Initiate program cycle"
        option["description"] = 'Initiate a new program cycle now.'
        system["options"].append(option)

        option = {}
        option["option"] = "Date/Time"
        option["description"] = 'Show Date & Time'
        system["options"].append(option)

        option = {}
        option["option"] = "Temporary file server"
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "File-server shuts down after..."
        other["selected"] = 60
        other["type"] = "dropdown"
        other["values"] = []

        value = {}
        value["1 Minute"] = 60
        other["values"].append(value)

        value = {}
        value["2 Minute"] = 120
        other["values"].append(value)

        value = {}
        value["5 Minute"] = 300
        other["values"].append(value)

        option["others"].append(other)

        # OTHERS
        other = {}
        other["name"] = "Directory"
        other["selected"] = "/home/rh/backendv1/log"
        other["type"] = "dropdown"
        other["values"] = []

        value = {}
        value["Log Files"] = "/home/rh/backendv1/log"
        other["values"].append(value)

        value = {}
        value["Ini File"] = "/home/rh/backendv1/ini"
        other["values"].append(value)

        option["others"].append(other)

        option["description"] = 'Opens a temporary file-server'
        system["options"].append(option)

        return system

    def get_failover(self, parameters):
        """ FAILOVER """

        failover = {}
        failover["label"] = "Failover"
        failover["icon"] = "ErrorIcon"
        failover["options"] = []

        option = {}
        option["option"] = "Reset all gateways"
        option["description"] = 'Reset all gateways'
        failover["options"].append(option)

        option = {}
        option["option"] = "Failover rule"
        option["description"] = 'Change failover rule.'
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Rule"
        other["type"] = "dropdown"
        other["selected"] = "allow"
        other["values"] = []

        value = {}
        value["Allow: Can be used as gateway/internet provider"] = "allow"
        other["values"].append(value)

        value = {}
        value["Force: Will be set as highest priority above anything else."] = "force"
        other["values"].append(value)

        value = {}
        value["Forbid: Will be ignored as internet provider"] = "forbid"
        other["values"].append(value)

        value = {}
        value["Reset: Reset to default (allow) or configured setting in the ini-files."] = "reset"
        other["values"].append(value)

        option["others"].append(other)


        # OTHERS
        other = {}
        other["name"] = "Failover"
        other["hint"] = "If current rule is not shown for the list items, "
        other["hint"] += "the interface should be currently be defaulted to allowed."
        other["hint"] += "<br><small>Keep in mind that the current rule state only gets "
        other["hint"] += "updated every 10 minutes (default value).</small>"
        other["type"] = "dropdown"
        other["values"] = []

        parameter_rows = parameters['value']['PARAMETERS'].copy()

        failover_array = self.get_parameters_value(parameter_rows, r'FAILOVER\d')
        failover_array = sorted(failover_array, key=lambda i: i[0])
        for f_arr in failover_array:

            value = {}
            value["{0} - {1} - {2}".format(f_arr[1]['INTERFACE'],
                                           f_arr[1]['DESCRIPTION'],
                                           f_arr[1]['GATEWAY'])] = f_arr[0]
            other["values"].append(value)

        if failover_array:
            f_arr = failover_array[0]
            other["selected"] = "{0}".format(f_arr[0])

        option["others"].append(other)

        failover["options"].append(option)

        return failover

    def get_nc(self, parameters, ntwconf):
        """ NETWORK CONFIGURATION """

        parameter_rows = parameters['value']['PARAMETERS'].copy()

        netconf = {}
        netconf["label"] = "Network Configuration"
        netconf["icon"] = "NetworkCheck"
        netconf["options"] = []

        option = {}
        option["option"] = "Ping"
        option["description"] = "Ping an IP"
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Number of pings"
        other["type"] = "dropdown"
        other["selected"] = 1
        other["values"] = []

        value = {}
        value['1'] = 1
        other["values"].append(value)

        value = {}
        value['2'] = 2
        other["values"].append(value)

        value = {}
        value['3'] = 3
        other["values"].append(value)

        value = {}
        value['5'] = 5
        other["values"].append(value)

        value = {}
        value['10'] = 10
        other["values"].append(value)

        option["others"].append(other)

        # OTHERS
        other = {}
        other["name"] = "Destination IP"
        other["type"] = "input"

        option["others"].append(other)

        # OTHERS
        other = {}
        other["name"] = "Interface"
        other["type"] = "groupdropdown"
        other["selected"] = ""
        other["values"] = []

        value = {}
        value['Not defined'] = [\
            {"value": "",
             "label": "No specific interface (default)"}
                               ]
        other["values"].append(value)


        ntwconf_rows = ntwconf['value']['NTWCONF'].copy()

        ntwconf_array = self.get_parameters_value(ntwconf_rows, r'enp\w*')
        ntwconf_array = sorted(ntwconf_array, key=lambda i: i[0])

        value = {}
        value["Untagged"] = []
        for ntconf in ntwconf_array:
            value["Untagged"].append({
                "value": '-I ' + ntconf[0],
                "label": "{0}, {1}, {2}".format(ntconf[0], ntconf[1]['IP'], ntconf[1]['Netmask'])
            })

        other["values"].append(value)

        ntwconf_array = self.get_parameters_value(ntwconf_rows, r'tun\d')
        ntwconf_array = sorted(ntwconf_array, key=lambda i: i[0])

        value = {}
        value["Tunnels (VPN)"] = []
        for ntconf in ntwconf_array:
            value["Tunnels (VPN)"].append({
                "value": '-I ' + ntconf[0],
                "label": "{0}, {1}, {2}".format(ntconf[0], ntconf[1]['IP'], ntconf[1]['Netmask'])
            })

        other["values"].append(value)

        ntwconf_array = self.get_parameters_value(parameter_rows, r'VLAN\d')
        ntwconf_array = sorted(ntwconf_array, key=lambda i: i[0])

        value = {}
        value["VLAN's"] = []
        for ntconf in ntwconf_array:

            description = ""
            if 'DESCRIPTION' in ntconf[1].keys():
                description = ntconf[1]['DESCRIPTION']

            value["VLAN's"].append({
                "value": '-I' + ntconf[0],
                "label": "{0}, {1}, {2}".format(ntconf[0],
                                                description,
                                                ntconf[1]['IP'])
            })

        other["values"].append(value)

        option["others"].append(other)

        netconf["options"].append(option)

        option = {}
        option["option"] = "Interfaces"
        option["description"] = "Check network-interfaces of OBU, including IP-addresses."
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Method"
        other["type"] = "dropdown"
        other["selected"] = 'nmap --iflist'
        other["values"] = []

        value = {}
        value["Nmap: Including routes"] = 'nmap --iflist'
        other["values"].append(value)

        value = {}
        value["Ip: New debian method"] = 'ip a'
        other["values"].append(value)

        value = {}
        value["Ifconfig: Old debian method"] = '/sbin/ifconfig'
        other["values"].append(value)

        option["others"].append(other)

        netconf["options"].append(option)

        option = {}
        option["option"] = "Routes"
        option["description"] = "Show routes, including gateways and metrics"
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Method"
        other["type"] = "dropdown"
        other["selected"] = 'ip route'
        other["values"] = []

        value = {}
        value["IP Route"] = 'ip route'
        other["values"].append(value)

        value = {}
        value["Route"] = '/sbin/route'
        other["values"].append(value)

        value = {}
        value["Nmap: Including interfaces"] = 'nmap --iflist'
        other["values"].append(value)

        value = {}
        value["Netstat: Kernel IP Routing table"] = 'netstat -r'
        other["values"].append(value)

        option["others"].append(other)

        netconf["options"].append(option)

        option = {}
        option["option"] = "Connections"
        option["description"] = "Show internet connections"
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Method"
        other["type"] = "dropdown"
        other["selected"] = 'netstat -tp'
        other["values"] = []

        value = {}
        value["Active internet connections"] = 'netstat -tp'
        other["values"].append(value)

        option["others"].append(other)

        netconf["options"].append(option)

        option = {}
        option["option"] = "Network statistics"
        option["description"] = "Show network statistics"
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Method"
        other["type"] = "dropdown"
        other["selected"] = 'netstat -i'
        other["values"] = []

        value = {}
        value["Netstat: Network statistics"] = 'netstat -i'
        other["values"].append(value)

        option["others"].append(other)

        netconf["options"].append(option)

        option = {}
        option["option"] = "Scan host"
        option["description"] = "Scan a host."
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Host to scan"
        other["type"] = "input"
        other["hint"] = "Type IP-address (e.g. 192.168.0.1), can also have a subnet to"
        other["hint"] = " scan whole subnet (e.g. 192.168.0.1/24)"
        option["others"].append(other)

        # OTHERS
        other = {}
        other["name"] = "Please select an option:"
        other["type"] = "dropdown"
        other["selected"] = '-F'
        other["values"] = []

        value = {}
        value["Fast scan"] = '-F'
        other["values"].append(value)

        value = {}
        value['Normal'] = ""
        other["values"].append(value)

        value = {}
        value["Ping scan"] = '-sP'
        other["values"].append(value)

        value = {}
        value["More output"] = '-v'
        other["values"].append(value)

        value = {}
        value["Even more output"] = '-vv'
        other["values"].append(value)

        option["others"].append(other)


        netconf["options"].append(option)

        return netconf

    def get_modem(self, vessel_id, device):
        """ MODEM """

        modem = {}
        modem["label"] = device['device']
        modem["icon"] = "Router"
        modem["options"] = []

        option = {}
        option["option"] = "Reboot"
        option["description"] = "Reboot device"
        modem["options"].append(option)

        option = {}
        option["option"] = "Beam Lock"
        option["description"] = "Lock modem satellite"
        modem["options"].append(option)

        option = {}
        option["option"] = "Beam Switch"
        option["description"] = "Switch to another VSAT-Beam."
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Please select the beam:"
        other["type"] = "dropdown"
        other["values"] = []

        values = self.couch_query.get_complete_values(
            vessel_id,
            device['device'],
            flag='one_doc'
        )

        general = values['value'][device['device']]['General']

        selected_flag = False

        for gen in general.keys():

            if re.findall(r'Beam\[\d*\]', str(gen)):

                num = gen[(gen.index('[') + 1): gen.index(']')]

                opt = str(general[gen]) + "(" + num + ")"

                value = {}
                value[opt] = num
                other["values"].append(value)

                if not selected_flag:

                    other["selected"] = num

                    selected_flag = True

        option["others"].append(other)

        modem["options"].append(option)

        option = {}
        option["option"] = "New Map"
        option["description"] = "Load new map for modem"
        modem["options"].append(option)

        option = {}
        option["option"] = "Remove Map"
        option["description"] = "Remove map for modem'"
        modem["options"].append(option)

        return modem

    def get_power_switch(self, vessel_id, device):
        """ POWERSWITCH """

        power = {}
        power["label"] = device['device']
        power["icon"] = "PowerInput"
        power["options"] = []

        option = {}
        option["option"] = "Reboot Outlet"
        option["description"] = "Reboot outlet"
        option["others"] = []

        # OTHERS
        other = {}
        other["name"] = "Outlet number"
        other["type"] = "dropdown"
        other["values"] = []

        values = self.couch_query.get_complete_values(
            vessel_id,
            device['device'],
            flag='one_doc'
        )

        outlets = list(values['value'][device['device']].keys())

        outlets.remove('General')
        outlets.sort()

        selected_flag = False

        if outlets:

            for outlet in outlets:

                if re.findall(r'outlet\d', outlet):

                    num = int(re.search(r'\d+', outlet).group())
                    val = {}
                    # value[str(num)] = values['value'][device['device']][outlet]['name']
                    val[str(num) + ' - ' + values['value'][device['device']][outlet]['name']] = num
                    other["values"].append(val)

                    if not selected_flag:

                        other["selected"] = num

                        selected_flag = True


        option["others"].append(other)

        power["options"].append(option)

        return power

    def get_item(self, devices, pattern):
        """Return Item"""

        data = []
        for device in devices:

            if re.findall(r'' + pattern + r'\d', device['doc']['device']):
                data.append(device['doc'])

        data = sorted(data, key=lambda i: i['device'])

        return data


    def get_parameters_value(self, parameters, pattern):
        """Return Parameters Value"""

        values = []

        for key in parameters.keys():

            if re.findall(r'' + pattern, key):

                values.append([
                    key, parameters[key]
                    ])

        return values
