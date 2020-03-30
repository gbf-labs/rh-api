# pylint: disable=no-self-use, too-many-locals, superfluous-parens, undefined-loop-variable
"""Format Alarm State"""
from library.common import Common
from library.postgresql_queries import PostgreSQL
from library.alarm.calculate_operator_result import CalculateOperatorResult
class FormatAlarmState(Common):
    """Class for FormatAlarmState"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for FormatAlarmState class"""

        self.postgres = PostgreSQL()
        self.calc_result = CalculateOperatorResult()
        super(FormatAlarmState, self).__init__()

    def get_current_alarm(self, datas):
        """Format Current Alarm"""

        final_result = {}
        for result in datas:
            length = len(result['datas'])
            alarm = []
            if length > 0 and result['message'] == "ok":
                alarms = result['datas'][length-1]
                alarms['message'] = self.alarm_remarks(alarms['value'])

                #REMOVE KEY VALUE
                del alarms['value']

                alarm.append(alarms)
            else:

                #RETURN PREVIOUS DATA STATUS

                alarm.append({
                    "timestamp": result['previous']['timestamp'],
                    "message": self.alarm_remarks(result['message']),
                    "remarks": self.calc_result.get_remarks(result['message'])
                    })

            result['datas'] = alarm

            #REMOVE PREVIOUS DATA
            del result['previous']

            final_result = result

        return final_result

    def get_alarm24(self, datas, end_time):
        """Format Alarm by 24 hours"""

        for result in datas:

            if result['datas'] and result['message'] == "ok":

                i = 0
                sequence = 1
                dlength = len(result['datas'])

                results = []

                #ADD SEQUENCE
                for res in result['datas']:

                    if(i > 0):

                        if not res['remarks'] == result['datas'][i-1]['remarks']:
                        #     sequence = sequence
                        # else:
                            sequence += 1
                    # else:
                    #     sequence = sequence

                    i += 1

                    results.append({
                        "timestamp": res['timestamp'],
                        "sequence": sequence,
                        "value": res['value']
                    })

                sequence_number = ({s['sequence'] for s in results})

                alarm_results = []

                #ARRANGE ALARM TIMESTAMP
                for seq in sequence_number:

                    tmp_data = [res['timestamp'] for res in results if res['sequence'] == seq]
                    value = [res['value'] for res in results if res['sequence'] == seq]

                    percentage = str(round((len(tmp_data)/dlength) * 100, 2))

                    min_timestamp = min(tmp_data)
                    max_timestamp = max(tmp_data)

                    if seq > 1:
                        min_timestamp = alarm_results[seq-2]['end_time']

                    alarm_results.append({
                        "start_time" : min_timestamp,
                        "end_time": max_timestamp,
                        "message": self.alarm_remarks(value[0]),
                        "remarks": self.calc_result.get_remarks(value[0]),
                        "percentage": percentage
                    })

                result['datas'] = alarm_results


            else:

                #DISPLAY PREVIOUS UP TO CURRENT TIMESTAMP
                formatted_data = [{
                    "start_time" : result['previous']['timestamp'],
                    "end_time": end_time,
                    "message": self.alarm_remarks(result['message']),
                    "remarks": self.calc_result.get_remarks(result['message']),
                    "percentage" : str(100.0)
                    }]
                result['datas'] = formatted_data

            del result['previous']
        return result

    def alarm_remarks(self, data):
        """Alarm Remarks"""

        if data is True:
            return "Alarm"

        if data is False:
            return "Ok"

        if data == "Unknown":
            return "Unknown"

        if data == "No Data":
            return "No Data"

        return "Invalid"

    def filter_current_status(self, datas):
        """ Filter current status """
        results = []
        for data in datas:

            if data['results']:
                data['results'] = self.filter_results(data['results'])
                results.append(data)
            else:
                results.append(data)

        return results

    def filter_results(self, results):
        """ Filter Results """

        status = ['Ok', 'No Data']
        result = []
        for res in results:
            if res['datas'][0]['message'] not in status:
                result.append(res)

        return result
