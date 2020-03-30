# pylint: disable=too-many-instance-attributes, no-self-use
"""Update Role"""
from flask import  request
from library.common import Common
from library.postgresql_queries import PostgreSQL

class UpdateVesselINIFiles(Common):
    """Class for Update Vessel INI Files"""

    # INITIALIZE
    def __init__(self):
        """The Constructor for Update Vessel INI Files class"""
        self.postgres = PostgreSQL()
        super(UpdateVesselINIFiles, self).__init__()

        self.vpn_token = '269c2c3706886d94aeefd6e7f7130ab08346590533d4c5b24ccaea9baa5211ec'
        self.backend_dir = '/home/rh/backendv1/'

    def update_vessel_inifiles(self):
        """
        This API is for Update Vessel INI Files
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
          - name: query
            in: body
            description: Update Vessel INI Files
            required: true
            schema:
              id: Update Vessel INI Files
              properties:
                datas:
                    type: json
                    example: {}
        responses:
          500:
            description: Error
          200:
            description: Update Vessel INI Files
        """
        data = {}

        # GET JSON REQUEST
        query_json = request.get_json(force=True)
        inidatas = query_json['datas']

        # GET HEADER
        token = request.headers.get('token')

        # CHECK TOKEN
        if not token == self.vpn_token:
            data["alert"] = "Invalid Token"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        if not self.update_vessel_ini_datas(inidatas):

            data["alert"] = "Please check your query!"
            data['status'] = 'Failed'

            # RETURN ALERT
            return self.return_data(data)

        data['message'] = "INI Files successfully updated!"
        data['status'] = "ok"
        return self.return_data(data)

    def update_vessel_ini_datas(self, inidatas):
        """Update INI Files"""
        if "web" in inidatas.keys():

            print("UPDATE VESSEL VERSION")
            bdir = "/home/rh/backendv1/config/branch.cfg"
            with open(bdir, "w") as filename:

                filename.write("[BRANCH]" + "\n")
                filename.write("web: " + str(inidatas["web"]) + "\n")
                filename.write("api: " + str(inidatas["api"]) + "\n")
                filename.write("backend: " + str(inidatas["backend"]) + "\n")

        else:

            for fname in inidatas.keys():
                fdir = self.backend_dir + fname
                with open(fdir, "w") as filename:
                    for line in inidatas[fname].split("\n"):

                        filename.write(line+"\n")

        # RETURN
        return 1
