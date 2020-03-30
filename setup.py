# pylint: disable=too-many-locals, line-too-long, too-many-statements, too-many-branches, too-many-instance-attributes, attribute-defined-outside-init
"""Set Up"""
from __future__ import print_function
import time
from configparser import ConfigParser

from library.config_parser import config_section_parser
from library.postgresql_queries import PostgreSQL
from library.sha_security import ShaSecurity

class Setup():
    """Class for Setup"""

    def __init__(self):
        """The constructor for Setup class"""
        self.sha_security = ShaSecurity()
        self.postgres = PostgreSQL()

        # INIT CONFIG
        self.config = ConfigParser()
        # CONFIG FILE
        self.config.read("config/config.cfg")

    def main(self):
        """Main"""
        time.sleep(30) # Don't Delete this is for Docker
        self.create_database()
        self.create_tables()
        self.create_default_entries()

    def create_database(self):
        """Create Database"""
        self.dbname = config_section_parser(self.config, "POSTGRES")['db_name']
        self.postgres.connection(True)
        self.postgres.create_database(self.dbname)
        self.postgres.close_connection()

        self.vpn_db_build = config_section_parser(self.config, "VPNDB")['build']

        if self.vpn_db_build.upper() == 'TRUE':

            self.my_ip = config_section_parser(self.config, "IPS")['my']
            self.user_vpn = config_section_parser(self.config, "IPS")['user_vpn']
            self.vessel_vpn = config_section_parser(self.config, "IPS")['vessel_vpn']

    def create_tables(self):
        """Create Tables"""

        # OPEN CONNECTION
        self.postgres.connection()

        # ACCOUNT TABLE
        query_str = "CREATE TABLE account (id serial PRIMARY KEY,"
        query_str += " username VARCHAR (50) UNIQUE NOT NULL, password VARCHAR (355) NOT NULL,"
        query_str += " email VARCHAR (355) UNIQUE NOT NULL, token VARCHAR (1000) NOT NULL,"
        query_str += " first_name VARCHAR (1000) , last_name VARCHAR (1000),"
        query_str += " vessel_vpn_state VARCHAR (355),"
        query_str += " middle_name VARCHAR (1000), default_value BOOLEAN,"
        query_str += " url VARCHAR (1000), reset_token VARCHAR (355), status BOOLEAN NOT NULL,"
        query_str += " state BOOLEAN NOT NULL, reset_token_date BIGINT, created_on BIGINT NOT NULL,"
        query_str += " update_on BIGINT, last_login BIGINT)"

        print("Create table: account")
        if self.postgres.exec_query(query_str):
            print("Account table successfully created!")

        # VESSEL TABLE
        query_str = "CREATE TABLE vessel (vessel_id VARCHAR (500) PRIMARY KEY,"
        query_str += " number VARCHAR (355),"
        query_str += " state VARCHAR (355),"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: vessel")
        if self.postgres.exec_query(query_str):
            print("Vessel table successfully created!")

        # ALTER VESSEL TABLE
        # DON'T MOVE ALTER
        query_str = "ALTER TABLE vessel ADD CONSTRAINT vessel_pk PRIMARY KEY (vessel_id)"

        print("Alter table: vessel")
        if self.postgres.exec_query(query_str):
            print("Vessel table successfully Alter!")

        # DEVICE TABLE
        query_str = "CREATE TABLE device (device_id VARCHAR (500),"
        query_str += " device VARCHAR (355),"
        query_str += " device_type VARCHAR (355),"
        query_str += " vessel_id VARCHAR (355) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: device")
        if self.postgres.exec_query(query_str):
            print("Devidce table successfully created!")

        # MODULE TABLE
        query_str = "CREATE TABLE module (module_id VARCHAR (500),"
        query_str += " module VARCHAR (355),"
        query_str += " vessel_id VARCHAR (355) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: module")
        if self.postgres.exec_query(query_str):
            print("Module table successfully created!")


        # OPTION TABLE
        query_str = "CREATE TABLE option (option_id VARCHAR (500),"
        query_str += " option VARCHAR (355),"
        query_str += " vessel_id VARCHAR (355) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: option")
        if self.postgres.exec_query(query_str):
            print("Option table successfully created!")

        # COMPANY TABLE
        query_str = "CREATE TABLE company (company_id serial PRIMARY KEY,"
        query_str += " company_name VARCHAR (355) UNIQUE NOT NULL,"
        query_str += " default_value BOOLEAN,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: company")
        if self.postgres.exec_query(query_str):
            print("Company table successfully created!")

        # SELECTED LABEL TABLE
        query_str = "CREATE TABLE selected_label (selected_label_id serial PRIMARY KEY,"
        query_str += " device_type VARCHAR (355), select_type VARCHAR (355), label VARCHAR (355),"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Selected label table: Selected label")
        if self.postgres.exec_query(query_str):
            print("Selected label table successfully created!")

        # SOURCE: https://stackoverflow.com/questions/9789736/how-to-implement-a-many-to-many-relationship-in-postgresql
        # ROLE TABLE
        query_str = "CREATE TABLE role (role_id serial PRIMARY KEY,"
        query_str += " role_name VARCHAR (355) UNIQUE NOT NULL,"
        query_str += " default_value BOOLEAN,"
        query_str += " role_details VARCHAR (1000),"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: role")
        if self.postgres.exec_query(query_str):
            print("Role table successfully created!")

        # PERMISSION TABLE
        query_str = "CREATE TABLE permission (permission_id serial PRIMARY KEY,"
        query_str += " permission_name VARCHAR (355) UNIQUE NOT NULL,"
        query_str += " permission_details VARCHAR (1000),"
        query_str += " default_value BOOLEAN,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: permission")
        if self.postgres.exec_query(query_str):
            print("Permission table successfully created!")

        # REPORT TEMP TABLE
        query_str = "CREATE TABLE report_temp (report_temp_id serial PRIMARY KEY,"
        query_str += " vessel_id VARCHAR (355) UNIQUE NOT NULL REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " report_data VARCHAR (5000),"
        query_str += " state BOOLEAN,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: report_temp")
        if self.postgres.exec_query(query_str):
            print("Report temp table successfully created!")

        if self.vpn_db_build.upper() == 'TRUE':

            # JOB TABLE
            query_str = "CREATE TABLE job (job_id serial PRIMARY KEY,"
            query_str += " account_id int REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
            query_str += " callback_url VARCHAR (355), data_url VARCHAR (355),"
            query_str += " token VARCHAR (355), status VARCHAR (355),"
            query_str += " vnp_server_ip VARCHAR (355), vpn_type VARCHAR (355),"
            query_str += " account_os VARCHAR (355),"
            query_str += " remark VARCHAR (500), message VARCHAR (500),"
            query_str += " directory VARCHAR (500), action VARCHAR (355),"
            query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

            print("Create table: job")
            if self.postgres.exec_query(query_str):
                print("Job table successfully created!")


            # VESSEL VPN JOB TABLE
            query_str = "CREATE TABLE vessel_vpn_job (vessel_vpn_job_id serial PRIMARY KEY,"
            query_str += " callback_url VARCHAR (355), token VARCHAR (355), status VARCHAR (355),"
            query_str += " vnp_server_ip VARCHAR (355), vpn_type VARCHAR (355),"
            query_str += " vessel_name VARCHAR (500), imo VARCHAR (500),"
            query_str += " remark VARCHAR (500), message VARCHAR (500),"
            query_str += " directory VARCHAR (500), action VARCHAR (355),"
            query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

            print("Create table: vessel_vpn_job")
            if self.postgres.exec_query(query_str):
                print("Vessel VPN Job table successfully created!")


        # EMAIL LOG TABLE
        query_str = "CREATE TABLE email_log (mail_log_id serial PRIMARY KEY,"
        query_str += " email_schedule_id BIGINT, email_vessel_id BIGINT,"
        query_str += " date_today BIGINT, message jsonb, data_date VARCHAR (355),"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: email_log")
        if self.postgres.exec_query(query_str):
            print("Vessel Email table successfully created!")

        # EMAIL VESSEL TABLE
        query_str = "CREATE TABLE email_vessel (email_vessel_id serial PRIMARY KEY,"
        query_str += " vessel_id VARCHAR (355) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " email VARCHAR (355),"
        query_str += " mail_enable BOOLEAN, reporting_enable BOOLEAN,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: email_vessel")
        if self.postgres.exec_query(query_str):
            print("Vessel Email table successfully created!")

        # EMAIL SCHEDULE TABLE
        query_str = "CREATE TABLE email_schedule (email_schedule_id serial PRIMARY KEY,"
        query_str += " email_vessel_id int REFERENCES email_vessel "
        query_str += "(email_vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " schedule VARCHAR (355), utc_time BIGINT,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: email_schedule")
        if self.postgres.exec_query(query_str):
            print("MAIL SCHEDULE table successfully created!")

        # ROLE PERMISSION TABLE
        query_str = "CREATE TABLE role_permission ("
        query_str += " role_id int REFERENCES role (role_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " permission_id int REFERENCES permission (permission_id) ON UPDATE CASCADE,"
        query_str += " CONSTRAINT role_permission_pkey PRIMARY KEY (role_id, permission_id))"

        print("Create table: role_permission")
        if self.postgres.exec_query(query_str):
            print("Role permission table successfully created!")

        # ACCOUNT VESSEL TABLE
        query_str = "CREATE TABLE account_vessel ("
        query_str += " account_id int REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " vessel_vpn_state VARCHAR (355), vessel_vpn_ip VARCHAR (355),"
        query_str += " vessel_id VARCHAR (1000) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " allow_access BOOLEAN)"

        print("Create table: account_vessel")
        if self.postgres.exec_query(query_str):
            print("Account vessel table successfully created!")

        # ACCOUNT OFF LINE VESSEL TABLE
        query_str = "CREATE TABLE account_offline_vessel ("
        query_str += " account_id int REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " vessel_vpn_state VARCHAR (355), vessel_vpn_ip VARCHAR (355),"
        query_str += " vessel_id VARCHAR (1000) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " allow_access BOOLEAN)"

        print("Create table: account_offline_vessel")
        if self.postgres.exec_query(query_str):
            print("Account vessel table successfully created!")

        # ACCOUNT VPN TABLE
        query_str = "CREATE TABLE account_vpn ("
        query_str += " account_id int REFERENCES account (id) ON DELETE CASCADE,"
        query_str += " vpn_type VARCHAR (350), vpn_ip VARCHAR (350), status BOOLEAN,"
        query_str += " created_on BIGINT NOT NULL)"

        print("Create table: account_vpn")
        if self.postgres.exec_query(query_str):
            print("Account VPN table successfully created!")

        # ACCOUNT ROLE TABLE
        query_str = "CREATE TABLE account_role ("
        query_str += " account_id int REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " role_id int REFERENCES role (role_id) ON UPDATE CASCADE,"
        query_str += " CONSTRAINT account_role_pkey PRIMARY KEY (account_id, role_id))"

        print("Create table: account_role")
        if self.postgres.exec_query(query_str):
            print("Account role table successfully created!")

        # ACCOUNT COMPANY TABLE
        query_str = "CREATE TABLE account_company ("
        query_str += " account_id int REFERENCES account (id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " company_id int REFERENCES company (company_id) ON UPDATE CASCADE,"
        query_str += " CONSTRAINT account_company_pkey PRIMARY KEY (account_id, company_id))"

        print("Create table: account_company")
        if self.postgres.exec_query(query_str):
            print("Account company table successfully created!")

        # INI FILES TABLE
        query_str = "CREATE TABLE ini_files (ini_files_id serial PRIMARY KEY,"
        query_str += " vessel_id VARCHAR (1000) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " dir VARCHAR (355), content jsonb,"
        query_str += " lastupdate BIGINT, vessel_lastupdate BIGINT,"
        query_str += " update_on BIGINT, created_on BIGINT NOT NULL)"

        print("Create table: ini_files")
        if self.postgres.exec_query(query_str):
            print("INI files table successfully created!")

        # VERSION TABLE
        query_str = "CREATE TABLE version (version_id serial PRIMARY KEY,"
        query_str += " version_name VARCHAR (100) UNIQUE NOT NULL, web VARCHAR (100),"
        query_str += " api VARCHAR (100), backend VARCHAR (100), status BOOLEAN NOT NULL,"
        query_str += " description VARCHAR (1000), created_on BIGINT NOT NULL)"

        print("Create table: version")
        if self.postgres.exec_query(query_str):
            print("Version table successfully created!")

        # LATEST VERSION TABLE
        query_str = "CREATE TABLE latest_version (latest_version_id bool PRIMARY KEY DEFAULT TRUE,"
        query_str += " version_id serial REFERENCES version (version_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " CONSTRAINT latest_version_uni CHECK (latest_version_id))"

        print("Create table: latest_version")
        if self.postgres.exec_query(query_str):
            print("Latest Version table successfully created!")

        # VESSEL VERSION TABLE
        query_str = "CREATE TABLE vessel_version"
        query_str += " (vessel_id VARCHAR (1000) UNIQUE NOT NULL REFERENCES vessel (vessel_id)"
        query_str += " ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " version_id serial REFERENCES version (version_id) ON UPDATE CASCADE ON DELETE CASCADE)"

        print("Create table: vessel_version")
        if self.postgres.exec_query(query_str):
            print("Vessel Version table successfully created!")

        # VESSEL VERSION LOG TABLE
        query_str = "CREATE TABLE vessel_version_log"
        query_str += " (vessel_id VARCHAR (1000) REFERENCES vessel (vessel_id)"
        query_str += " ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " version_id serial REFERENCES version (version_id) ON UPDATE CASCADE ON DELETE CASCADE,"
        query_str += " created_on BIGINT NOT NULL)"

        print("Create table: vessel_version_log")
        if self.postgres.exec_query(query_str):
            print("Vessel Version Log table successfully created!")

        # COMPANY VESSEL REF TABLE
        query_str = """ CREATE TABLE public.company_vessels (
                        company_id int4 NOT NULL,
                        vessel_id VARCHAR (500) NOT NULL REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE,
                        CONSTRAINT company_vessels_pkey PRIMARY KEY (company_id, vessel_id),
                        CONSTRAINT company_vessels_company_id_fkey FOREIGN KEY (company_id)
                            REFERENCES company(company_id) ON UPDATE CASCADE ON DELETE CASCADE
                   );"""

        print("Create table: company_vessels")
        if self.postgres.exec_query(query_str):
            print("Account Vessels Ref table successfully created!")

        #ALARM VALUE TABLE
        query_str = """CREATE TABLE alarm_value (alarm_value_id serial PRIMARY KEY,
                        name VARCHAR (255) NOT NULL,
                        vessel VARCHAR (255),
                        device VARCHAR (255),
                        device_type VARCHAR (255),
                        module VARCHAR (255),
                        option VARCHAR(255),
                        value VARCHAR (255),
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: alarm_value")
        if self.postgres.exec_query(query_str):
            print("Alarm value table successfully created!")

        #ALARM CONDITION OPERATOR TABLE
        query_str = """CREATE TABLE alarm_coperator
                    (alarm_coperator_id serial PRIMARY KEY, 
                        operator VARCHAR (255) UNIQUE NOT NULL,
                        param_num VARCHAR (255) NOT NULL,
                        label VARCHAR (255) NOT NULL,
                        opgroup VARCHAR (255) NOT NULL
                    );"""

        print("Create table: alarm_coperator")
        if self.postgres.exec_query(query_str):
            print("Alarm Condition Operator table successfully created!")

        #ALARM CONDITION TABLE
        query_str = """CREATE TABLE alarm_condition (alarm_condition_id serial PRIMARY KEY,
                        comment VARCHAR (255) NOT NULL,
                        operator_id INT REFERENCES alarm_coperator (alarm_coperator_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        parameters jsonb NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: alarm_condition")
        if self.postgres.exec_query(query_str):
            print("Alarm Condition table successfully created!")

        #ALARM TRIGGER TABLE
        query_str = """CREATE TABLE alarm_type (alarm_type_id serial PRIMARY KEY,
                        alarm_type VARCHAR(25) UNIQUE NOT NULL,
                        alarm_value INT
                    );"""

        print("Create table: alarm_type")
        if self.postgres.exec_query(query_str):
            print("Alarm Type table successfully created!")

        #ALARM TRIGGER TABLE
        query_str = """CREATE TABLE alarm_trigger (alarm_trigger_id serial PRIMARY KEY,
                        alarm_type_id int REFERENCES alarm_type (alarm_type_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        alarm_condition_id int REFERENCES alarm_condition (alarm_condition_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        alarm_enabled BOOLEAN DEFAULT 'f' NOT NULL,
                        label VARCHAR(255) NOT NULL,
                        description VARCHAR(255),
                        is_acknowledged BOOLEAN DEFAULT 'f' NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: alarm_trigger")
        if self.postgres.exec_query(query_str):
            print("Alarm Trigger table successfully created!")

        #ALARM DATA TABLE
        query_str = """CREATE TABLE alarm_data (alarm_data_id serial PRIMARY KEY,
                        alarm_trigger_id int REFERENCES alarm_trigger (alarm_trigger_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        average jsonb, device VARCHAR(555), 
                        module VARCHAR(555), option VARCHAR(555),
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        vessel_name VARCHAR(555),
                        alarm_description VARCHAR(555), err_message VARCHAR(555),
                        device_id VARCHAR(555), message VARCHAR(555),
                        alarm_type VARCHAR(555),
                        vessel_number VARCHAR(555), alarm_type_id int 
                        REFERENCES alarm_type (alarm_type_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        epoch_date BIGINT NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: alarm_data")
        if self.postgres.exec_query(query_str):
            print("Alarm Data table successfully created!")

        #ALARM STATE TABLE
        query_str = """CREATE TABLE alarm_state (alarm_state_id serial PRIMARY KEY,
                        alarm_trigger_id int REFERENCES alarm_trigger (alarm_trigger_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        category VARCHAR(50),
                        results jsonb, device VARCHAR(555), 
                        module VARCHAR(555), option VARCHAR(555),
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        vessel_name VARCHAR(555),
                        alarm_description VARCHAR(555), err_message VARCHAR(555),
                        device_id VARCHAR(555), message VARCHAR(555),
                        alarm_type VARCHAR(555),
                        vessel_number VARCHAR(555), alarm_type_id int 
                        REFERENCES alarm_type (alarm_type_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        epoch_date BIGINT NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: alarm_state")
        if self.postgres.exec_query(query_str):
            print("Alarm Data table successfully created!")

        # VESSEL IMAGE TABLE
        query_str = """CREATE TABLE vessel_image (vessel_image_id serial PRIMARY KEY,
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        vessel_imo VARCHAR(555),
                        image_name VARCHAR(555),
                        status VARCHAR(10) NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: vessel_image")
        if self.postgres.exec_query(query_str):
            print("Vessel image table successfully created!")

        # VESSEL FILE TABLE
        query_str = """CREATE TABLE vessel_file (vessel_file_id serial PRIMARY KEY,
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        vessel_imo VARCHAR(555),
                        file_name VARCHAR(555),
                        status VARCHAR(10) NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: vessel_file")
        if self.postgres.exec_query(query_str):
            print("Vessel file table successfully created!")

        # BLOCKAGE DATA TABLE
        query_str = """CREATE TABLE blockage_data (blockage_data_id serial PRIMARY KEY,
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        device_id VARCHAR(555),
                        antenna_status jsonb NOT NULL,
                        coordinates jsonb NOT NULL,
                        blockzones jsonb NOT NULL,
                        epoch_date BIGINT NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: blockage_data")
        if self.postgres.exec_query(query_str):
            print("Blockage Data table successfully created!")

        # SUBCATEGORY TABLE
        query_str = """CREATE TABLE subcategory (subcategory_id serial PRIMARY KEY,
                        subcategory_name VARCHAR(255) UNIQUE NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: subcategory")
        if self.postgres.exec_query(query_str):
            print("Sub Category table successfully created!")

        # SUBCATEGORY OPTION TABLE
        query_str = """CREATE TABLE subcategory_options (subcategory_id INT REFERENCES subcategory (subcategory_id) ON UPDATE CASCADE ON DELETE CASCADE,
                        option VARCHAR(255) UNIQUE NOT NULL
                    );"""

        print("Create table: subcategory_options")
        if self.postgres.exec_query(query_str):
            print("Sub Category Options table successfully created!")

        # DEVICE IMAGE TABLE
        query_str = """CREATE TABLE device_image (device_image_id serial PRIMARY KEY,
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        device_id VARCHAR(255), 
                        vessel_imo VARCHAR(555),
                        image_name VARCHAR(555),
                        status VARCHAR(10) NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""

        print("Create table: device_image")
        if self.postgres.exec_query(query_str):
            print("Device image table successfully created!")

        #ALARM EMAIL TABLE
        query_str = """CREATE TABLE alarm_email (alarm_email_id serial PRIMARY KEY,
                        alarm_trigger_id int REFERENCES alarm_trigger (alarm_trigger_id) 
                        ON UPDATE CASCADE ON DELETE CASCADE,
                        vessel_id VARCHAR(555) REFERENCES vessel (vessel_id) ON UPDATE CASCADE ON DELETE CASCADE, 
                        device_id VARCHAR(555), alarm_status VARCHAR(100), message jsonb,
                        epoch_date BIGINT NOT NULL,
                        created_on BIGINT NOT NULL,
                        update_on BIGINT
                    );"""
        print("Create table: alarm_email")
        if self.postgres.exec_query(query_str):
            print("Alarm Email table successfully created!")

        # ALTER TABLE ACCOUNT VPN
        query_str = "ALTER TABLE account_vpn ADD COLUMN job_id BIGINT"

        print("ALTER TABLE account vpn")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE account vpn successfully!")


        # ALTER TABLE ALARM VALUE
        query_str = "ALTER TABLE alarm_value ADD CONSTRAINT unique_name UNIQUE(name)"

        print("ALTER TABLE alarm_value")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE alarm_value successfully!")
        else:
            print("Failed to ALTER ALARM VALUE")

        # ALTER TABLE ALARM CONDITION
        query_str = "ALTER TABLE alarm_condition ADD CONSTRAINT unique_comment UNIQUE(comment)"

        print("ALTER TABLE alarm_condition")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE alarm_condition successfully!")
        else:
            print("Failed to ALTER ALARM CONDITION")

        # ALTER TABLE ALARM TRIGGER
        query_str = "ALTER TABLE alarm_trigger  ADD CONSTRAINT unique_label UNIQUE(label)"

        print("ALTER TABLE alarm_trigger")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE alarm_trigger successfully!")
        else:
            print("Failed to ALTER ALARM TRIGGER")

        # ALTER TABLE ACCOUNT
        query_str = "ALTER TABLE account ADD COLUMN is_active BOOLEAN"

        print("ALTER TABLE account")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE account successfully!")
        else:
            print("Failed to ALTER account")

        # ALTER TABLE VESSEL
        query_str = "ALTER TABLE vessel ADD COLUMN vessel_name VARCHAR(555)"

        print("ALTER TABLE vessel")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE vessel successfully!")
        else:
            print("Failed to ALTER vessel")

        # ALTER TABLE ALARM TRIGGER
        query_str = "ALTER TABLE alarm_trigger"
        query_str += " ADD COLUMN alarm_email BOOLEAN DEFAULT 'f' NOT NULL,"
        query_str += " ADD COLUMN email VARCHAR (255)"

        print("ALTER TABLE alarm_trigger")
        if self.postgres.exec_query(query_str):
            print("ALTER TABLE alarm_trigger successfully!")
        else:
            print("Failed to ALTER alarm_trigger")

        # UPDATE TABLE ACCOUNT
        query_str = "UPDATE account SET is_active=true WHERE is_active IS NULL"

        print("UPDATE TABLE account")
        if self.postgres.exec_query(query_str):
            print("UPDATE TABLE account successfully!")
        else:
            print("Failed to UPDATE account table")

        # CLOSE CONNECTION
        self.postgres.close_connection()

    def create_default_entries(self):
        """Create Default Entries"""
        vpn_db_build = config_section_parser(self.config, "VPNDB")['build']

        # PERMISSION
        data = {}
        data['permission_name'] = config_section_parser(self.config, "PERMISSION")['permission_name']
        data['permission_details'] = config_section_parser(self.config, "PERMISSION")['permission_details']
        data['default_value'] = True
        data['created_on'] = time.time()


        print("Create default permission: ", data['permission_name'])
        permission_id = self.postgres.insert('permission', data, 'permission_id')

        count = 9

        if vpn_db_build.upper() == 'TRUE':

            count = 10

        for dta in range(1, count):

            data1 = {}
            data1['permission_name'] = config_section_parser(self.config, "PERMISSION")['permission_name' + str(dta)]
            data1['permission_details'] = config_section_parser(self.config, "PERMISSION")['permission_details' + str(dta)]
            data1['default_value'] = True
            data1['created_on'] = time.time()

            print("Create default permission: ", data1['permission_name'])
            self.postgres.insert('permission', data1, 'permission_id')

        if permission_id:

            print("Default Permission successfully created!")

        else:

            self.postgres.connection()

            sql_str = "SELECT * FROM permission WHERE permission_name='" + data['permission_name'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            permission_id = res['permission_id']

            self.postgres.close_connection()

        # ROLE
        data = {}
        data['role_name'] = config_section_parser(self.config, "ROLE")['role_name']
        data['role_details'] = config_section_parser(self.config, "ROLE")['role_details']
        data['default_value'] = True
        data['created_on'] = time.time()

        # ROLE1
        data1 = {}
        data1['role_name'] = config_section_parser(self.config, "ROLE")['role_name1']
        data1['role_details'] = config_section_parser(self.config, "ROLE")['role_details1']
        data1['default_value'] = True
        data1['created_on'] = time.time()

        # ROLE2
        data2 = {}
        data2['role_name'] = config_section_parser(self.config, "ROLE")['role_name2']
        data2['role_details'] = config_section_parser(self.config, "ROLE")['role_details2']
        data2['default_value'] = True
        data2['created_on'] = time.time()

        if vpn_db_build.upper() == 'TRUE':

            # ROLE3
            data3 = {}
            data3['role_name'] = config_section_parser(self.config, "ROLE")['role_name3']
            data3['role_details'] = config_section_parser(self.config, "ROLE")['role_details3']
            data3['default_value'] = True
            data3['created_on'] = time.time()

        print("Create default role: ", data['role_name'])
        print("Create default role: ", data1['role_name'])
        print("Create default role: ", data2['role_name'])
        role_id = self.postgres.insert('role', data, 'role_id')
        self.postgres.insert('role', data1, 'role_id')
        self.postgres.insert('role', data2, 'role_id')

        if vpn_db_build.upper() == 'TRUE':
            print("Create default role: ", data3['role_name'])
            self.postgres.insert('role', data3, 'role_id')
            sa_role_id = self.postgres.insert('role', data3, 'role_id')

        if role_id:
            print("Default Role successfully created!")
        else:
            self.postgres.connection()

            sql_str = "SELECT * FROM role WHERE role_name='" + data['role_name'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            role_id = res['role_id']

            self.postgres.close_connection()

        if vpn_db_build.upper() == 'TRUE':

            if sa_role_id:
                print("Default Role successfully created!")
            else:
                self.postgres.connection()

                sql_str = "SELECT * FROM role WHERE role_name='" + data3['role_name'] + "'"
                res = self.postgres.query_fetch_one(sql_str)
                sa_role_id = res['role_id']

                self.postgres.close_connection()

        # ROLE PERMISSION
        temp = {}
        temp['role_id'] = role_id
        temp['permission_id'] = permission_id
        self.postgres.insert('role_permission', temp)

        # SUPER ADMIN
        # ROLE PERMISSION
        self.postgres.connection()

        sql_str = "SELECT permission_id FROM permission WHERE permission_name ='all and with admin vessel VPN.'"
        permission = self.postgres.query_fetch_one(sql_str)

        self.postgres.close_connection()

        if vpn_db_build.upper() == 'TRUE':

            temp = {}
            temp['role_id'] = sa_role_id
            temp['permission_id'] = permission['permission_id']
            self.postgres.insert('role_permission', temp)

        # ACCOUNT
        data = {}
        data['username'] = config_section_parser(self.config, "ADMIN")['username']
        data['password'] = config_section_parser(self.config, "ADMIN")['password']
        data['email'] = config_section_parser(self.config, "ADMIN")['email']
        data['status'] = bool(config_section_parser(self.config, "ADMIN")['status'])
        data['state'] = bool(config_section_parser(self.config, "ADMIN")['state'])
        data['url'] = "default"
        data['token'] = self.sha_security.generate_token()
        data['default_value'] = True
        data['created_on'] = time.time()
        data['update_on'] = time.time()

        print("Create default user: ", data['username'])
        account_id = self.postgres.insert('account', data, 'id')
        if account_id:
            print("Default user successfully created!")
        else:
            self.postgres.connection()

            sql_str = "SELECT id FROM account WHERE username='" + data['username'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            account_id = res['id']

            self.postgres.close_connection()

        # ACCOUNT ROLE
        temp = {}
        temp['account_id'] = account_id
        temp['role_id'] = role_id
        self.postgres.insert('account_role', temp)

        # COMPANY
        data = {}
        data['company_name'] = config_section_parser(self.config, "COMPANY")['company_name']
        data['default_value'] = True
        data['created_on'] = time.time()

        print("Create default company: ", data['company_name'])
        company_id = self.postgres.insert('company', data, 'company_id')
        if company_id:
            print("Default Role successfully created!")
        else:
            self.postgres.connection()

            sql_str = "SELECT * FROM company WHERE company_name='" + data['company_name'] + "'"
            res = self.postgres.query_fetch_one(sql_str)
            company_id = res['company_id']

            self.postgres.close_connection()

        # ACCOUNT COMPANY
        temp = {}
        temp['account_id'] = account_id
        temp['company_id'] = role_id
        self.postgres.insert('account_company', temp)

        #ALARM TYPE
        temp = {}
        alarm_types = ({"alarm_type": "Critical", "alarm_value" : 10},
                       {"alarm_type": "Warning", "alarm_value" : 20},
                       {"alarm_type": "Alert", "alarm_value" : 30},
                       {"alarm_type": "Info", "alarm_value" : 40},
                       {"alarm_type": "Debug", "alarm_value" : 50})

        for data in alarm_types:
            alarm_type_id = self.postgres.insert('alarm_type', data)
            if alarm_type_id:
                print("Alarm types successfully added!")
            else:
                print("Failed to add Alarm Type")

        temp = {}
        alarm_operators = ({"operator":"TRUE", "param_num": 0, "label": "Always True", "opgroup": "Boolean"},
                           {"operator":"FALSE", "param_num": 0, "label": "Always False", "opgroup": "Boolean"},
                           {"operator":"!", "param_num": 1, "label": "Invert Boolean-result", "opgroup": "Boolean"},
                           {"operator":"=", "param_num": 2, "label": "True if equal", "opgroup": "Boolean"},
                           {"operator":"!=", "param_num": 2, "label": "True if Param1 not equal to Param2", "opgroup": "Boolean"},
                           {"operator":"LIKE", "param_num": 2, "label": "True if Param1 LIKE Param2 case insensitive", "opgroup": "String"},
                           {"operator":"!LIKE", "param_num": 2, "label": "True if Param1 not LIKE Param2 case insensitive", "opgroup": "String"},
                           {"operator":">", "param_num": 2, "label": "True if Param1 > Param2", "opgroup": "Boolean"},
                           {"operator":"<", "param_num": 2, "label": "True if Param1 < Param2", "opgroup": "Boolean"},
                           {"operator":"AND", "param_num": 2, "label": "True if Param1 AND Param2 are true", "opgroup": "Boolean"},
                           {"operator":"OR", "param_num": 2, "label": "True if Param1 OR Param2 is true", "opgroup": "Boolean"},
                           {"operator":"+", "param_num": 2, "label": "Returns the sum of Param1 and Param2", "opgroup": "Double"},
                           {"operator":"-", "param_num": 2, "label": "Returns the difference of Param1 and Param2", "opgroup": "Double"},
                           {"operator":"*", "param_num": 2, "label": "Returns the Param1 times Param2", "opgroup": "Double"},
                           {"operator":"/", "param_num": 2, "label": "Returns the Param1 divided by Param2", "opgroup": "Double"},
                           {"operator":"BETWEEN", "param_num": 3, "label": "True if Param1 > Param2 and Param1 < Param3", "opgroup": "Boolean"},
                           {"operator":"BETWEENEQ", "param_num": 3, "label": "True if Param1 >= Param2 and Param1 =< Param3", "opgroup": "Boolean"},
                           {"operator":"!BETWEEN", "param_num": 3, "label": "True if Param1 < Param2 and Param1 > Param3", "opgroup": "Boolean"},
                           {"operator":"!BETWEENEQ", "param_num": 3, "label": "True if Param1 <= Param2 and Param1 >= Param3", "opgroup": "Boolean"})

        for data in alarm_operators:
            alarm_operator_id = self.postgres.insert('alarm_coperator', data)
            if alarm_operator_id:
                print("Alarm Conditions successfully added!")
            else:
                print("Failed to add Alarm Conditions")

if __name__ == '__main__':

    # INIT CONFIG
    CONFIG = ConfigParser()
    # CONFIG FILE
    CONFIG.read("config/config.cfg")

    SERVER_TYPE = config_section_parser(CONFIG, "SERVER")['server_type']

    if SERVER_TYPE != 'production':
        SETUP = Setup()
        SETUP.main()

    else:

        print("YOU'RE TRYING TO UPDATE LIVE SERVER!!!")

#drop table device;
#drop table module;
#drop table option;
#drop table report_temp;
#drop table email_schedule;
#drop table email_vessel;
#drop table account_vessel;
#drop table account_offline_vessel;
#drop table company_vessels;
#drop table alarm_data;
#drop table vessel;
