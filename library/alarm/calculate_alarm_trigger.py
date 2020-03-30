# pylint: disable=too-many-arguments, unidiomatic-typecheck
"""Calculate Alarm Trigger"""
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm.calculate_alarm_condition import CalculateAlarmCondition
from library.alarm.alarm_type import AlarmType

class CalculateAlarmTrigger(Common):
    """Class for CalculateAlarmTrigger"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CalculateAlarmTrigger class"""

        self.postgres = PostgreSQL()
        self.calc_condition = CalculateAlarmCondition()
        self.alarm_type = AlarmType()
        super(CalculateAlarmTrigger, self).__init__()

    def calculate_trigger(self, trigger_ids, start, end, vessel_id=None, device_id=None):
        """Calculate Alarm Trigger"""

        results = []

        if vessel_id:
            check_vessel = self.validate_vessel_device(vessel_id, "vessel")
            if not check_vessel:
                return "Invalid Vessel."

        if device_id:
            check_device = self.validate_vessel_device(device_id, "device")
            if not check_device:

                # CHECK BY DEVICE NAME
                device_id = self.validate_device_name(device_id)

                if not device_id:
                    return "Invalid Device."

        for trigger_id in trigger_ids:

            alarm_trigger = self.get_alarm_trigger(trigger_id)
            # print("*"*50)
            # print("alarm_trigger: ", alarm_trigger)
            # print("*"*50)
            if alarm_trigger:

                alarm_type = self.alarm_type.alarm_type(alarm_trigger['alarm_type_id'])

                # CALCULATE CONDITION
                result = self.calc_condition.calculate_condition(
                    alarm_trigger['alarm_condition_id'],
                    start, end, vessel_id, device_id)
                # print("+"*50)
                # print("result: ", result)
                # print("+"*50)
                if type(result) == list:

                    #REMOVE COREVALUES TIMESTAMP
                    for res in result:
                        del res['core']

                        res['alarm_trigger_id'] = alarm_trigger['alarm_trigger_id']

                    results.append({
                        "results":result,
                        "err_message": "",
                        "alarm_trigger_id": alarm_trigger['alarm_trigger_id'],
                        "alarm_type_id": alarm_trigger['alarm_type_id'],
                        "alarm_type": alarm_type['alarm_type'],
                        "alarm_description": alarm_trigger['description']
                        })

                else:

                    results.append({
                        "results":[],
                        "err_message": result,
                        "alarm_trigger_id": alarm_trigger['alarm_trigger_id'],
                        "alarm_type_id": alarm_trigger['alarm_type_id'],
                        "alarm_type": alarm_type['alarm_type'],
                        "alarm_description": alarm_trigger['description']
                        })

            # Pylint Error -> Redefinition of results type from list to str
            # (redefined-variable-type)
            # else:
                # results = "No Alarm Trigger found."

        return results

    # GET ALARM TRIGGER
    def get_alarm_trigger(self, alarm_trigger_id):
        """Get Alarm Trigger"""

        assert alarm_trigger_id, "Alarm Trigger ID is required."

        # OPEN CONNECTION
        self.postgres.connection()

        # DATA
        sql_str = "SELECT * FROM alarm_trigger"
        sql_str += " WHERE alarm_trigger_id={0}".format(alarm_trigger_id)
        alarm_trigger = self.postgres.query_fetch_one(sql_str)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        if alarm_trigger:

            return alarm_trigger

        return 0

    def validate_vessel_device(self, _id, key):
        """Validate Vessel and Device"""

        assert _id, "{0} ID is required.".format(key.upper())

        # OPEN CONNECTION
        self.postgres.connection()

        # DATA
        sql_str = "SELECT * FROM {0}".format(key)
        sql_str += " WHERE {0}_id= '{1}'".format(key, _id)
        data = self.postgres.query_fetch_one(sql_str)

        # CLOSE CONNECTION
        self.postgres.close_connection()

        if data:

            return 1

        return 0


    def validate_device_name(self, device):
        """Validate Device Name"""

        assert device, "{0} Device name is required."


        sql_str = "SELECT device_id FROM device"
        sql_str += " WHERE device = '{0}'".format(device.upper())
        data = self.postgres.query_fetch_one(sql_str)


        if data:

            return data['device_id']

        return 0
