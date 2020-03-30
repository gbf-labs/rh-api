"""Version"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class Version(Common):
    """Class for Version"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Version class"""
        self.postgres = PostgreSQL()
        super(Version, self).__init__()

    def version(self):
        """
        This API is for Getting Version
        ---
        tags:
          - Version
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
        responses:
          500:
            description: Error
          200:
            description: Version
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        datas = self.get_version()

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_version(self):
        """Return Version"""

        sql_str = "SELECT * FROM version"
        versions = self.postgres.query_fetch_all(sql_str)

        sql_str = "SELECT * FROM latest_version"
        latest_version = self.postgres.query_fetch_one(sql_str)
        lv_id = latest_version["version_id"]

        final_data = []
        for ver in versions:

            ver["latest"] = False

            if ver['version_id'] == lv_id:

                ver["latest"] = True

            final_data.append(ver)

        data = {}
        data['rows'] = versions

        return data
