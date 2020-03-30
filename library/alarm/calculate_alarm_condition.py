# pylint: disable=too-many-arguments, too-many-locals, bad-option-value, redefined-variable-type
"""Calculate Alarm Condition"""
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm.calculate_alarm_value import CalculateAlarmValue
from library.alarm.calculate_operator_result import CalculateOperatorResult

class CalculateAlarmCondition(Common):
    """Class for CalculateAlarmCondition"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CalculateAlarmCondition class"""
        self.postgres = PostgreSQL()
        self.calc_value = CalculateAlarmValue()
        self.calc_result = CalculateOperatorResult()
        super(CalculateAlarmCondition, self).__init__()

    def calculate_condition(self, condition_id, start, end, vessel_id=None, device_id=None):
        """Calculate Alarm Condition"""

        if condition_id:

            #GET OPERATOR
            alarm_condition = self.get_alarm_condition(condition_id)

            operator_id = int(alarm_condition['operator_id'])
            operator = self.get_alarm_operator(operator_id)

            param_length = alarm_condition['param_length']
            parameters = alarm_condition['parameters']

            #GET NUMBER OF PARAMETERS BY OPERATOR
            operator_param_number = int(self.get_param_number(operator_id))

            if operator_param_number != param_length:

                result = "Parameters not match"

            else:

                params = [param['type'] for param in parameters]

                if not "conditions" in params and  not "values" in params:
                    result = "No alarm value or condition selected"

                else:
                    #GET PARAMETER VALUES
                    param_values = []

                    for param in parameters:

                        param_result = self.calc_condition_parameter(param, start, end,
                                                                     vessel_id, device_id)

                        if not param_result:

                            return "No Data to Show"

                        param_values.append(param_result)

                    result = self.calc_result.calculate_operator_result(operator, param_values)

        return result

    #GET PARAMETER NUMBER
    def  get_param_number(self, operator):
        """Get Number of Parameters"""

        # DATA
        sql_str = "SELECT param_num FROM alarm_coperator"
        sql_str += " WHERE alarm_coperator_id ='{0}'".format(operator)

        param = self.postgres.query_fetch_one(sql_str)

        if param:

            return param['param_num']

        return ''

    # GET ALARM CONDITION
    def get_alarm_condition(self, alarm_condition_id):
        """Get Alarm Condition"""

        assert alarm_condition_id, "Alarm Condition ID is required."

        # DATA
        sql_str = "SELECT *, jsonb_array_length(parameters) as param_length FROM alarm_condition"
        sql_str += " WHERE alarm_condition_id={0}".format(alarm_condition_id)
        alarm_condition = self.postgres.query_fetch_one(sql_str)

        return alarm_condition

    #CALCULATE PARAMETER
    def calc_condition_parameter(self, parameter, start, end, vessel_id=None, device_id=None):
        """Calculate Alarm Condition Parameter"""

        result = 0

        if parameter:

            if parameter['type'] == "values":

                # CALCULATE ALARM VALUE
                result = self.calc_value.calculate_value(parameter['id'], start, end,
                                                         vessel_id, device_id)

            elif parameter['type'] == "conditions":

                #CALCULATE ALARM CONDITION
                result = self.calculate_condition(parameter['id'], start, end,
                                                  vessel_id, device_id)

            elif not parameter['type']:
                #GET INPUT DATA
                result = [str(parameter['label'])]

            else:

                result = ''

        return result


    # GET ALARM CONDITION OPERATOR
    def get_alarm_operator(self, alarm_coperator_id):
        """Get Alarm Operator"""

        assert alarm_coperator_id, "Alarm Condition Operator ID is required."

        # DATA
        sql_str = "SELECT operator FROM alarm_coperator"
        sql_str += " WHERE alarm_coperator_id={0}".format(alarm_coperator_id)
        alarm_coperator = self.postgres.query_fetch_one(sql_str)

        return alarm_coperator['operator']
