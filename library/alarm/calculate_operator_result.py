# pylint: disable=no-self-use, too-many-arguments, too-many-locals, bad-option-value, too-many-branches, too-many-nested-blocks, eval-used, redefined-variable-type
"""Calculate Operator Result"""
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.couch_queries import Queries

class CalculateOperatorResult(Common):
    """Class for CalculateOperatorResult"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for CalculateOperatorResult class"""
        self.postgres = PostgreSQL()
        self.couch_query = Queries()
        super(CalculateOperatorResult, self).__init__()

    def calculate_operator_result(self, comparator, params):
        """Calculate Operator Result"""

        if len(params) == 1:

            for param in params:
                result = self.compute_operator(param, comparator)

        if len(params) == 2:

            result = self.split_params(params, comparator)

        if len(params) == 3:

            params1 = [params[0], params[1]]
            params2 = [params[0], params[2]]

            if comparator == "BETWEEN":

                param_result1 = self.split_params(params1, ">")
                param_result2 = self.split_params(params2, "<")

            elif comparator == "BETWEENEQ":

                param_result1 = self.split_params(params1, ">=")
                param_result2 = self.split_params(params2, "<=")

            elif comparator == "!BETWEEN":

                param_result1 = self.split_params(params1, "<")
                param_result2 = self.split_params(params2, ">")

            elif comparator == "!BETWEENQ":

                param_result1 = self.split_params(params1, "<=")
                param_result2 = self.split_params(params2, ">=")

            param_results = [param_result1, param_result2]

            result = self.split_params(param_results, "AND")

        return result

    def check_param_content(self, params):
        """Check Parameter Content"""

        temp_data = []
        for param in params:

            if any("datas" in x for x in param) or any("result" in x for x in param):
                indicator = "datas"
            else:
                indicator = "input"

            temp_data.append({
                "indicator" : indicator,
                "data" : param
                })

        return temp_data

    def split_params(self, params, comparator):
        """Split Parameters"""
        result = []

        param_content = self.check_param_content(params)

        if param_content[0]['indicator'] == "input" and param_content[1]['indicator'] == "datas":

            swap = True
            result = self.analyze_param(params[1], params[0], comparator, swap)

        elif param_content[0]['indicator'] == "input" and param_content[1]['indicator'] == "input":

            if not 'No Data to Show' in params:

                for param1 in params[0]:
                    for param2 in params[1]:
                        results = self.compute_operator(param1, comparator, param2)

                result.append({
                    "value": results,
                    "remarks" : self.get_remarks(results)
                    })

        else:
            swap = False
            result = self.analyze_param(params[0], params[1], comparator, swap)

        return result

    def analyze_param(self, param1, param2, comparator, swap=None):
        """Analyze Parameter"""

        results = []

        for param in param1:

            parameter1 = param['datas']

            core = param['core']
            previous_core = param['previous']
            vessel_name = self.check_vessel_name(param['vessel_id'])
            vessel_data = self.check_vessel_number(param['vessel_id'])

            if len(core) > 0:

                if param['message'] == "ok":

                    parameter2 = ""

                    if any("datas" in x for x in param2):

                        indicator = "multiple"

                        for par2 in param2:

                            if param['vessel_id'] == par2['vessel_id']:
                                if len(par2['datas']) != 0:
                                    parameter2 = par2['datas']
                    else:

                        indicator = "none"
                        parameter2 = param2

                    if not parameter2:

                        continue

                    parameter = [parameter1, parameter2]

                    # CHECK DEVICE IF FAILOVER
                    if param['device'].upper() == "FAILOVER":

                        result = self.compute_failover_param(parameter, comparator,
                                                             swap, flag=indicator)
                    else:
                        result = self.compute_param(parameter, comparator, core,
                                                    previous_core, swap, flag=indicator)

                    datas = sorted(result, key=lambda i: i["timestamp"])

                else:

                    datas = [{
                        "timestamp" : previous_core['timestamp'],
                        "value": previous_core['remarks'],
                        "remarks": self.get_remarks(param['message'])
                    }]

                results.append({
                    "vessel_id": param['vessel_id'],
                    "vessel_name": vessel_name,
                    "vessel_number": vessel_data,
                    "device": param['device'],
                    "device_id": param['device_id'],
                    "core": param['core'],
                    "previous": previous_core,
                    "message": param['message'],
                    "module": param['module'],
                    "option": param['option'],
                    "datas": datas
                    })
            else:

                datas = [{
                    "timestamp" : previous_core['timestamp'],
                    "value": previous_core['remarks'],
                    "remarks": self.get_remarks(previous_core['remarks'])
                }]

                results.append({
                    "vessel_id": param['vessel_id'],
                    "vessel_name": vessel_name,
                    "vessel_number": vessel_data,
                    "device": param['device'],
                    "device_id": param['device_id'],
                    "core": param['core'],
                    "previous": previous_core,
                    "message": previous_core['remarks'],
                    "module": param['module'],
                    "option": param['option'],
                    "datas": datas
                    })

        return results

    def compute_param(self, params, comparator, cores, prevcore, swap=None, flag=None):
        """Compute Parameter"""

        results = []

        param1 = params[0]
        param2 = params[1]

        for core in cores:

            if not param1:

                res = ""

                if prevcore['remarks'] in ['Unknown', 'ok']:
                    remarks = "Unknown"

                else:
                    remarks = "No Data"


                results.append({
                    "timestamp" : core,
                    "value": res,
                    "remarks": self.get_remarks(remarks)
                    })

            else:

                parameter1 = [param['timestamp'] for param in param1]

                try:
                    check_param1 = parameter1.index(core)

                    timestamp = param1[check_param1]['timestamp']
                    val1 = param1[check_param1]['value']

                    if flag == "multiple":

                        parameter2 = [p['timestamp'] for p in param2]

                        try:
                            check_param2 = parameter2.index(core)
                            val2 = param2[check_param2]['value']

                            if swap is True:
                                res = self.compute_operator(val2, comparator, val1)
                            else:
                                res = self.compute_operator(val1, comparator, val2)

                        except ValueError:
                            res = "Unknown"

                    else:
                        if not param2:
                            res = "Unknown"

                        else:

                            for par2 in param2:

                                val2 = self.check_data_type(par2)

                                if swap is True:
                                    res = self.compute_operator(val2, comparator, val1)
                                else:
                                    res = self.compute_operator(val1, comparator, val2)

                    results.append({
                        "timestamp" :timestamp,
                        "value": res,
                        "remarks" : self.get_remarks(res)
                        })

                except ValueError:

                    res = "Unknown"
                    results.append({
                        "timestamp" : core,
                        "value": res,
                        "remarks": "Unknown"
                        })

        return results

    def get_remarks(self, data):
        """Get Remarks"""

        if data is True:

            return "red"

        if data is False:

            return "green"

        if data == "Unknown":

            return "orange"

        if data == "No Data":

            return "blue"

        return "violet"

    def check_data_type(self, data):
        """Check Data Type"""

        try:

            if data in ['True', 'False']:
                formatted = eval(data)

            elif data.lstrip("-").isdigit():
                formatted = float(int(data))

            else:
                formatted = float(data)

            return formatted

        except ValueError:

            return data

    def check_vessel_name(self, vessel_id):
        """Check Vessel Name"""

        if vessel_id:
            vessel_name = self.couch_query.get_complete_values(
                vessel_id,
                "PARAMETERS"
            )
            if vessel_name:
                return vessel_name['PARAMETERS']['INFO']['VESSELNAME']

            return "Vessel Not Found"

        return 0


    def check_vessel_number(self, vessel_id):
        """Check Vessel Number"""

        data = self.couch_query.get_by_id(vessel_id)

        if data:

            if "error" in data:

                return "No Data Found"

            return data['number']
        return "No Data Found"

    def compute_failover_param(self, params, comparator, swap=None, flag=None):
        """Compute Failover Parameter"""

        results = []

        param1 = params[0]
        param2 = params[1]

        for param in param1:
            timestamp = param['timestamp']

            if param['value'] is None:
                res = "Unknown"
            else:
                val1 = self.check_data_type(param['value'])

                if flag == "multiple":

                    parameter2 = [p['timestamp'] for p in param2]

                    try:
                        check_param2 = parameter2.index(param)
                        val2 = self.check_data_type(param2[check_param2]['value'])

                        if swap is True:
                            res = self.compute_operator(val2, comparator, val1)
                        else:
                            res = self.compute_operator(val1, comparator, val2)

                    except ValueError:
                        res = "Unknown"

                else:

                    if not param2:
                        res = "Unknown"

                    else:

                        for par2 in param2:

                            val2 = self.check_data_type(par2)

                            if swap is True:
                                res = self.compute_operator(val2, comparator, val1)
                            else:
                                res = self.compute_operator(val1, comparator, val2)

            results.append({
                "timestamp" :timestamp,
                "value": res,
                "remarks" : self.get_remarks(res)
            })

        return results
