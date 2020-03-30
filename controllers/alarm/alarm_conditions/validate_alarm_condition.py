# pylint: disable=too-few-public-methods
"""Validate Alarm Condition"""
from library.common import Common
from library.alarm.calculate_alarm_condition import CalculateAlarmCondition

class ValidateAlarmCondition(Common):
    """Class for ValidateAlarmCondition"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for ValidateAlarmCondition class"""
        self.calc_condition = CalculateAlarmCondition()
        super(ValidateAlarmCondition, self).__init__()

    def validate_alarm_condition(self, query_json):
        """Validate Alarm Condition"""

        data = {}

        if not query_json['comment']:
            data["alert"] = "Comment cannot be empty!"
            return data

        if not query_json['operator_id']:
            data["alert"] = "Operator cannot be empty!"
            return data

        if query_json['operator_id']:
            if query_json['operator_id'] == "0":
                data["alert"] = "Invalid Operator ID!"

            else:
                opt_param_number = int(self.calc_condition.get_param_number(
                    query_json['operator_id']))

                param_length = len(query_json['parameters'])

                if  param_length != opt_param_number:

                    data["alert"] = "Parameter not match"

                else:

                    params = [param['type'] for param in query_json['parameters']]

                    if not "conditions" in params and  not "values" in params:

                        data["alert"] = "Please select alarm value or condition"

        return data
