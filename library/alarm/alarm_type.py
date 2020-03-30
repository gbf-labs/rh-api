# pylint: disable=too-few-public-methods
"""Alarm Type"""
from library.common import Common
from library.postgresql_queries import PostgreSQL

class AlarmType(Common):
    """Class for AlarmType"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for AlarmType class"""
        self.postgres = PostgreSQL()
        super(AlarmType, self).__init__()

    # GET ALARM TRIGGER
    def alarm_type(self, alarm_type_id):
        """Get Alarm Types"""

        assert alarm_type_id, "Alarm Condition ID is required."

        # DATA
        alarm_type = []
        sql_str = "SELECT * FROM alarm_type WHERE alarm_type_id={0}".format(alarm_type_id)
        alarm_type = self.postgres.query_fetch_one(sql_str)

        return alarm_type
