"""Role"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class INIFiles(Common):
    """Class for INI Files"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for INI Files class"""
        self.postgres = PostgreSQL()
        super(INIFiles, self).__init__()

    def ini_files(self):
        """
        This API is for Getting INI Files
        ---
        tags:
          - INI Files
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
        responses:
          500:
            description: Error
          200:
            description: INI Files
        """
        data = {}

        # GET DATA
        token = request.headers.get('token')
        userid = request.headers.get('userid')
        vessel_id = request.args.get('vessel_id')

        # CHECK TOKEN
        token_validation = self.validate_token(token, userid)

        if not token_validation:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        datas = self.get_ini_files(vessel_id)

        datas['status'] = 'ok'

        return self.return_data(datas)

    def get_ini_files(self, vessel_id):
        """Return INI Files"""

        # GET SUPER ADMIN ID
        sql_str = "SELECT * FROM ini_files WHERE vessel_id ='{0}'".format(vessel_id)
        ini_files = self.postgres.query_fetch_all(sql_str)

        datas = {}

        for ini_file in ini_files:

            datas[ini_file['dir']] = "\n".join(ini_file['content'])

        final_data = {}
        final_data['filenames'] = [x['dir'] for x in ini_files]
        final_data['datas'] = datas

        return final_data
