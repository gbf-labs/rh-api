"""THIS SCRIPT IS FOR RHBOX API"""
import os
# import time
# import jsonify
# import request
import atexit

from configparser import ConfigParser

from flask import Flask
from flasgger import Swagger
# from flasgger.utils import swag_from
from flask_cors import CORS #, cross_origin
from apscheduler.schedulers.background import BackgroundScheduler

from library.config_parser import config_section_parser
from library.log import Log

# USER CONTROLLER
from controllers.user import user
from controllers.user import login
from controllers.user import invite
from controllers.user import reinvite
from controllers.user import update_user
from controllers.user import disable_user
from controllers.user import delete_user
from controllers.user import enable_user
from controllers.user import user_profile
from controllers.user import user_client
from controllers.user import user_company
from controllers.user import authentication_key
from controllers.user import reset_password

# VESSEL CONTROLLER
from controllers.vessel import vessel_data
from controllers.vessel import core_values
from controllers.vessel import vessels
from controllers.vessel import parameters
from controllers.vessel import network_performance
from controllers.vessel import network_configuration
from controllers.vessel import failover
from controllers.vessel import report_update
from controllers.vessel import report
from controllers.vessel import update_vessel_state
from controllers.vessel import create_vessel
from controllers.vessel import delete_vessel
from controllers.vessel import vessel_vpn_update

# MAP CONTROLLER
from controllers.map import map_vessel

# VESSEL CONTROLLER
from controllers.vessel.image import upload as vessel_image_upload
from controllers.vessel.image import delete as vessel_image_delete
from controllers.vessel.file import upload as vessel_file_upload
from controllers.vessel import vessel_files
from controllers.vessel.file import delete as vessel_file_delete

# VESSEL EMAIL SCHEDULE CONTROLLER
from controllers.email import update_email_schedule
from controllers.email import noon_report
from controllers.email import noon_report_data
from controllers.email import noon_report_pdf
from controllers.email import noon_report_csv


# INI FILES CONTROLLER
from controllers.inifiles import inifiles
from controllers.inifiles import update_inifiles
from controllers.inifiles import vessel_inifiles_update

# DEVICE CONTROLLER
from controllers.device import device
from controllers.device import device_state
from controllers.device import general_info
from controllers.device import port_forwarding
from controllers.device.image import upload as device_image_upload
from controllers.device.image import delete as device_image_delete
from controllers.device.image import images as device_images
from controllers.device import device_list

# ALARM VALUE CONTROLLER
from controllers.alarm.alarm_values import create_alarm_value
from controllers.alarm.alarm_values import update_alarm_value
from controllers.alarm.alarm_values import delete_alarm_value
from controllers.alarm.alarm_values import alarm_value_data
from controllers.alarm.alarm_values import alarm_values

# ALARM CONDITION CONTROLLER
from controllers.alarm.alarm_conditions import create_alarm_condition
from controllers.alarm.alarm_conditions import update_alarm_condition
from controllers.alarm.alarm_conditions import delete_alarm_condition
from controllers.alarm.alarm_conditions import alarm_conditions

# ALARM TRIGGER CONTROLLER
from controllers.alarm.alarm_triggers import create_alarm_trigger
from controllers.alarm.alarm_triggers import update_alarm_trigger
from controllers.alarm.alarm_triggers import delete_alarm_trigger
from controllers.alarm.alarm_triggers import alarm_triggers

# ALARM TYPE CONTROLLER
from controllers.alarm.alarm_types import alarm_types

# ALARM CONDITION OPERATOR CONTROLLER
from controllers.alarm.alarm_conditions import alarm_condition_operator

# ALARM CONDITION PARAMETERS CONTROLLER
from controllers.alarm.alarm_conditions import alarm_condition_parameters

# ALARM STATE CONTROLLER
from controllers.alarm.alarm_state import alarm_state
from controllers.alarm.alarm_state import alarm_state_overview

# ALARM OBU SUMMARY CONTROLLER
from controllers.alarm.obu_summary import obu_summary
from controllers.alarm.obu_summary import device_overview

# STATISTICS CONTROLLER
# from controllers.statistics import statistics

# ANNOUNCEMENT CONTROLLER
from controllers.announcement import announcement

# PERMISSION CONTROLLER
from controllers.permission import permission
from controllers.permission import create_permission
from controllers.permission import update_permission
from controllers.permission import delete_permission

# PERMISSION CONTROLLER
from controllers.role import role
from controllers.role import create_role
from controllers.role import update_role
from controllers.role import delete_role

# COMPANY CONTROLLER
from controllers.company import company
from controllers.company import create_company
from controllers.company import update_company
from controllers.company import delete_company

# GRAPH CORE VALUES CONTROLLER
from controllers.graph import graph
from controllers.graph import graph_selected

# REMOTE COMMAND CONTROLLER
from controllers.remote_command import rc_system
from controllers.remote_command import remote_command

# VPN CONTROLLER
from controllers.vpn_data import vpn_data
from controllers.vpn_data import vpn_update

# DASHBOARD CONTROLLER
from controllers.dashboard import dashboard

# BLOCKAGE MAP CONTROLLER
from controllers.blockage import blockage

# CATEGORY CONTROLLER
from controllers.category import subcategory
from controllers.category import create_subcategory
from controllers.category import update_subcategory
from controllers.category import delete_subcategory
from controllers.category import subcategory_option

# VERSION CONTROL
from controllers.version import version
from controllers.version import create_version
from controllers.version import set_version

LOG = Log()

APP = Flask(__name__)


# INIT CONFIG
CONFIG = ConfigParser()

# CONFIG FILE
CONFIG.read("config/config.cfg")

# cross_origin(origin='localhost',headers=['Content- Type','Authorization'])

CORS(APP)
# CORS(APP, supports_credentials=True)

Swagger(APP)

# ENVIRONMENT VARIABLES
os.environ["database"] = "couchdb"

# --------------------------------------------------------------
# USER
# --------------------------------------------------------------
USER = user.User()
LOGIN = login.Login()
INVITE = invite.Invite()
REINVITE = reinvite.Reinvite()
UPDATE_USER = update_user.UpdateUser()
DISABLE_USER = disable_user.DisableUser()
DELETE_USER = delete_user.DeleteUser()
ENABLE_USER = enable_user.EnableUser()
USER_PROFILE = user_profile.UserProfile()
USER_CLIENT = user_client.UserClient()
USER_COMPANY = user_company.UserCompany()
AUTHENTICATION_KEY = authentication_key.AuthenticationKey()
RESET_PASSWORD = reset_password.ResetPassword()

# USER ROUTE
APP.route('/user/index', methods=['GET'])(USER.user)
APP.route('/user/login', methods=['POST'])(LOGIN.login)
APP.route('/user/invite', methods=['POST'])(INVITE.invitation)
APP.route('/user/reinvite', methods=['POST'])(REINVITE.reinvite)
APP.route('/user/update', methods=['PUT'])(UPDATE_USER.update_user)
APP.route('/user/disable', methods=['PUT'])(DISABLE_USER.disable_user)
APP.route('/user/delete', methods=['DELETE'])(DELETE_USER.delete_user)
APP.route('/user/enable', methods=['PUT'])(ENABLE_USER.enable_user)
APP.route('/user/profile', methods=['GET'])(USER_PROFILE.user_profile)
APP.route('/user/clients', methods=['GET'])(USER_CLIENT.user_client)
APP.route('/user/company', methods=['GET'])(USER_COMPANY.user_company)
APP.route('/user/authentication/key', methods=['PUT'])(AUTHENTICATION_KEY.authentication_key)
APP.route('/user/reset/password', methods=['PUT'])(RESET_PASSWORD.reset_password)

# --------------------------------------------------------------
# VESSEL
# --------------------------------------------------------------
VESSEL_DATA = vessel_data.Vessel()
CORE_VALUES = core_values.CoreValues()
VESSELS = vessels.Vessels()
PARAMETERS = parameters.Parameters()
NETWORK_PERFORMANCE = network_performance.NetworkPerformance()
NETWORK_CONFIGURATION = network_configuration.NetworkConfiguration()
FAILOVER = failover.Failover()
REPORT_UPDATE = report_update.ReportUpdate()
REPORT = report.Report()
UPDATE_VESSEL_STATE = update_vessel_state.UpdateVesselState()
CREATE_VESSEL = create_vessel.CreateVessel()
DELETE_VESSEL = delete_vessel.DeleteVessel()
VESSEL_VPN_UPDATE = vessel_vpn_update.VesselVPNUpdate()
VESSEL_IMAGE_UPLOAD = vessel_image_upload.Upload()
VESSEL_IMAGE_DELETE = vessel_image_delete.Delete()
VESSEL_FILE_UPLOAD = vessel_file_upload.Upload()
VESSEL_FILE_LIST = vessel_files.VesselFiles()
VESSEL_FILE_DELETE = vessel_file_delete.Delete()

# VESSEL ROUTE
APP.route('/vessels', methods=['GET'])(VESSELS.all_vessels)
APP.route('/vessels/data', methods=['GET'])(VESSEL_DATA.get_vessels_data)
APP.route('/vessels/parameters', methods=['GET'])(PARAMETERS.parameters)
APP.route('/vessels/core/values', methods=['GET'])(CORE_VALUES.core_values)
APP.route('/vessels/network/performance',
          methods=['GET'])(NETWORK_PERFORMANCE.network_performance)
APP.route('/vessels/network/configuration',
          methods=['GET'])(NETWORK_CONFIGURATION.network_configuration)
APP.route('/vessels/failover', methods=['GET'])(FAILOVER.failover)
APP.route('/vessels/report/update', methods=['PUT'])(REPORT_UPDATE.report_update)
APP.route('/vessels/report', methods=['GET'])(REPORT.report)
APP.route('/vessels/state/update', methods=['PUT'])(UPDATE_VESSEL_STATE.update_vessel_state)
APP.route('/vessels/create', methods=['POST'])(CREATE_VESSEL.create_vessel)
APP.route('/vessels/delete', methods=['DELETE'])(DELETE_VESSEL.delete_vessel)
APP.route('/vessels/vpn/update', methods=['PUT'])(VESSEL_VPN_UPDATE.vessel_vpn_update)
APP.route('/vessels/image', methods=['POST'])(VESSEL_IMAGE_UPLOAD.image_upload)
APP.route('/vessels/image/delete', methods=['DELETE'])(VESSEL_IMAGE_DELETE.delete_image)
APP.route('/vessels/file', methods=['POST'])(VESSEL_FILE_UPLOAD.file_upload)
APP.route('/vessels/file/list', methods=['GET'])(VESSEL_FILE_LIST.get_files)
APP.route('/vessels/file/delete', methods=['DELETE'])(VESSEL_FILE_DELETE.delete_file)

# --------------------------------------------------------------
# MAP
# --------------------------------------------------------------
MAP_VESSEL = map_vessel.MapVessels()

# MAP ROUTE
APP.route('/map/vessels', methods=['GET'])(MAP_VESSEL.map_vessels)

# --------------------------------------------------------------
# VESSEL EMAIL SCHEDULE
# --------------------------------------------------------------
UPDATE_EMAIL_SCHEDULE = update_email_schedule.UpdateEmailSchedule()
NOON_REPORT = noon_report.NoonReport()
NOON_REPORT_DATA = noon_report_data.NoonReportData()
NOON_REPORT_PDF = noon_report_pdf.NoonReportPDF()
NOON_REPORT_CSV = noon_report_csv.NoonReportCSV()

APP.route('/email/schedule/update', methods=['PUT'])(UPDATE_EMAIL_SCHEDULE.update_email_schedule)
APP.route('/email/noon/report', methods=['GET'])(NOON_REPORT.noon_report)
APP.route('/email/noon/report/data', methods=['GET'])(NOON_REPORT_DATA.noon_report_data)
APP.route('/email/noon/report/pdf', methods=['GET'])(NOON_REPORT_PDF.noon_report_pdf)
APP.route('/email/noon/report/csv', methods=['GET'])(NOON_REPORT_CSV.noon_report_csv)

# --------------------------------------------------------------
# VESSEL INI FILES
# --------------------------------------------------------------
INIFILES = inifiles.INIFiles()
UPDATE_INIFILES = update_inifiles.UpdateINIFiles()
VESSEL_INIFILES_UPDATE = vessel_inifiles_update.UpdateVesselINIFiles()

APP.route('/ini/files', methods=['GET'])(INIFILES.ini_files)
APP.route('/update/ini/files', methods=['PUT'])(UPDATE_INIFILES.update_inifiles)
APP.route('/vessel/ini/files', methods=['PUT'])(VESSEL_INIFILES_UPDATE.update_vessel_inifiles)

# --------------------------------------------------------------
# DEVICE
# --------------------------------------------------------------
DEVICE = device.Device()
DEVICE_STATE = device_state.DeviceState()
GENERAL_INFO = general_info.GeneralInfo()
PORT_FORWARDING = port_forwarding.PortForwarding()
DEVICE_IMAGE_UPLOAD = device_image_upload.Upload()
DEVICE_IMAGE_DELETE = device_image_delete.Delete()
DEVICE_IMAGE_LIST = device_images.DeviceImages()
DEVICE_LIST = device_list.DeviceList()

# DEVICE ROUTE
APP.route('/device/list', methods=['GET'])(DEVICE.device_list)
# APP.route('/device/info', methods=['GET'])(device_state.device_state)
APP.route('/device/state', methods=['GET'])(DEVICE_STATE.device_state)
APP.route('/device/list/general/info', methods=['GET'])(GENERAL_INFO.general_info)
APP.route('/device/port/forwarding', methods=['GET'])(PORT_FORWARDING.port_forwarding)
APP.route('/device/image/upload', methods=['POST'])(DEVICE_IMAGE_UPLOAD.device_upload)
APP.route('/device/image/delete', methods=['DELETE'])(DEVICE_IMAGE_DELETE.delete_device_image)
APP.route('/device/image/list', methods=['GET'])(DEVICE_IMAGE_LIST.get_images)
APP.route('/device/devicelist', methods=['GET'])(DEVICE_LIST.get_list)
# --------------------------------------------------------------
# ALARM TRIGGER TYPES
# --------------------------------------------------------------
# ALARM TRIGGER TYPES CONTROLLER
# from controllers.alarm import alarm_trigger_types
# alarm_trigger_types = alarm_trigger_types.AlarmTriggerTypes()

# # ALARM TRIGGER TYPES ROUTE
# APP.route('/alarm/trigger/types', methods=['GET'])(alarm_trigger_types.get_alarm_trigger_types)

# --------------------------------------------------------------
# ALARM VALUE
# --------------------------------------------------------------
ALARM_VALUE_CREATE = create_alarm_value.CreateAlarmValue()
ALARM_VALUE_UPDATE = update_alarm_value.UpdateAlarmValue()
ALARM_VALUE_DELETE = delete_alarm_value.DeleteAlarmValue()
ALARM_VALUE_DATA = alarm_value_data.AlarmValueData()
ALARM_VALUE = alarm_values.AlarmValues()

# ALARM VALUE ROUTE
APP.route('/alarm/value/create', methods=['POST'])(ALARM_VALUE_CREATE.create_alarm_value)
APP.route('/alarm/value/update', methods=['PUT'])(ALARM_VALUE_UPDATE.update_alarm_value)
APP.route('/alarm/value/delete', methods=['DELETE'])(ALARM_VALUE_DELETE.delete_alarm_value)
APP.route('/alarm/value/data', methods=['GET'])(ALARM_VALUE_DATA.alarm_value_data)
APP.route('/alarm/value/index', methods=['GET'])(ALARM_VALUE.alarm_values)

# --------------------------------------------------------------
# ALARM CONDITION
# --------------------------------------------------------------
ALARM_CONDITION_CREATE = create_alarm_condition.CreateAlarmCondition()
ALARM_CONDITION_UPDATE = update_alarm_condition.UpdateAlarmCondition()
ALARM_CONDITION_DELETE = delete_alarm_condition.DeleteAlarmCondition()
ALARM_CONDITION = alarm_conditions.AlarmConditions()

# ALARM TRIGGER ROUTE
APP.route('/alarm/condition/create',
          methods=['POST'])(ALARM_CONDITION_CREATE.create_alarm_condition)
APP.route('/alarm/condition/update',
          methods=['PUT'])(ALARM_CONDITION_UPDATE.update_alarm_condition)
APP.route('/alarm/condition/delete',
          methods=['DELETE'])(ALARM_CONDITION_DELETE.delete_alarm_condition)
APP.route('/alarm/condition/index',
          methods=['GET'])(ALARM_CONDITION.alarm_conditions)

# --------------------------------------------------------------
# ALARM TRIGGER
# --------------------------------------------------------------
ALARM_TRIGGER_CREATE = create_alarm_trigger.CreateAlarmTrigger()
ALARM_TRIGGER_UPDATE = update_alarm_trigger.UpdateAlarmTrigger()
ALARM_TRIGGER_DELETE = delete_alarm_trigger.DeleteAlarmTrigger()
ALARM_TRIGGER = alarm_triggers.AlarmTriggers()

# ALARM TRIGGER ROUTE
APP.route('/alarm/trigger/create', methods=['POST'])(ALARM_TRIGGER_CREATE.create_alarm_trigger)
APP.route('/alarm/trigger/update', methods=['PUT'])(ALARM_TRIGGER_UPDATE.update_alarm_trigger)
APP.route('/alarm/trigger/delete', methods=['DELETE'])(ALARM_TRIGGER_DELETE.delete_alarm_trigger)
APP.route('/alarm/trigger/index', methods=['GET'])(ALARM_TRIGGER.alarm_triggers)

# --------------------------------------------------------------
# ALARM TYPE
# --------------------------------------------------------------
ALARM_TYPE = alarm_types.AlarmTypes()

# ALARM TYPE ROUTE
APP.route('/alarm/type/index', methods=['GET'])(ALARM_TYPE.alarm_types)

# --------------------------------------------------------------
# ALARM CONDITION OPERATION
# --------------------------------------------------------------
ALARM_CONDITION_OPERATOR = alarm_condition_operator.AlarmConditionOperator()

# ALARM OPERATORS ROUTE
APP.route('/alarm/operators/index',
          methods=['GET'])(ALARM_CONDITION_OPERATOR.alarm_condition_operators)

# --------------------------------------------------------------
# ALARM CONDITION PARAMETER
# --------------------------------------------------------------
ALARM_CONDITION_PARAMETER = alarm_condition_parameters.AlarmConditionParameters()

# ALARM CONDITION PARAMETERS ROUTE
APP.route('/alarm/parameters/index',
          methods=['GET'])(ALARM_CONDITION_PARAMETER.alarm_condition_parameters)

# --------------------------------------------------------------
# ALARM STATE
# --------------------------------------------------------------
ALARM_STATE = alarm_state.AlarmState()
ALARM_STATE_OVERVIEW = alarm_state_overview.AlarmStateOverview()

# ALARM STATE ROUTE
APP.route('/alarm/state/index', methods=['GET'])(ALARM_STATE.alarm_state)
APP.route('/alarm/state/overview', methods=['GET'])(ALARM_STATE_OVERVIEW.alarm_state_overview)

# --------------------------------------------------------------
# ALARM SUMMARY
# --------------------------------------------------------------
OBU_SUMMARY = obu_summary.ObuSummary()
DEVICE_OVERVIEW = device_overview.DeviceOverview()

# ALARM OBU SUMMARY ROUTE
APP.route('/alarm/summary/index', methods=['GET'])(OBU_SUMMARY.obu_summary)
APP.route('/alarm/device-overview', methods=['GET'])(DEVICE_OVERVIEW.device_overview)

# ALARM REPORT
# from controllers.alarm.report import percentage
# report_pecentage = percentage.Percentage()
# APP.route('/alarm/report/percentage', methods=['GET'])(report_pecentage.report_pecentage)

# # --------------------------------------------------------------
# # STATISTICS
# # --------------------------------------------------------------
# STATISTICS = statistics.Statistics()

# # STATISTICS ROUTE
# APP.route('/statistics', methods=['GET'])(STATISTICS.get_statistics)

# --------------------------------------------------------------
# ANNOUNCEMENT
# --------------------------------------------------------------
ANNOUNCEMENT = announcement.Announcement()

# ANNOUNCEMENT ROUTE
APP.route('/announcement', methods=['GET'])(ANNOUNCEMENT.get_announcement)

# --------------------------------------------------------------
# PERMISSION
# --------------------------------------------------------------
PERMISSION = permission.Permission()
CREATE_PERMISSION = create_permission.CreatePermission()
UPDATE_PERMISSION = update_permission.UpdatePermission()
DELETE_PERMISSION = delete_permission.DeletePermission()

# PERMISSION ROUTE
APP.route('/permission/index', methods=['GET'])(PERMISSION.permission)
APP.route('/permission/create', methods=['POST'])(CREATE_PERMISSION.create_permission)
APP.route('/permission/update', methods=['PUT'])(UPDATE_PERMISSION.update_permission)
APP.route('/permission/delete', methods=['DELETE'])(DELETE_PERMISSION.delete_permission)

# --------------------------------------------------------------
# PERMISSION
# --------------------------------------------------------------
ROLE = role.Role()
CREATE_ROLE = create_role.CreateRole()
UPDATE_ROLE = update_role.UpdateRole()
DELETE_ROLE = delete_role.DeleteRole()

# PERMISSION ROUTE
APP.route('/role/index', methods=['GET'])(ROLE.role)
APP.route('/role/create', methods=['POST'])(CREATE_ROLE.create_role)
APP.route('/role/update', methods=['PUT'])(UPDATE_ROLE.update_role)
APP.route('/role/delete', methods=['DELETE'])(DELETE_ROLE.delete_role)

# --------------------------------------------------------------
# COMPANY
# --------------------------------------------------------------
COMPANY = company.Company()
CREATE_COMPANY = create_company.CreateCompany()
UPDATE_COMPANY = update_company.UpdateCompany()
DELETE_COMPANY = delete_company.DeleteCompany()

# COMPANY ROUTE
APP.route('/company/index', methods=['GET'])(COMPANY.company)
APP.route('/company/create', methods=['POST'])(CREATE_COMPANY.create_company)
APP.route('/company/update', methods=['PUT'])(UPDATE_COMPANY.update_company)
APP.route('/company/delete', methods=['DELETE'])(DELETE_COMPANY.delete_company)


# --------------------------------------------------------------
# GRAPH CORE VALUES
# --------------------------------------------------------------
GRAPH = graph.Graph()
GRAPH_SELECTED = graph_selected.GraphSelected()

# GRAPH CORE VALUES ROUTE
APP.route('/graph', methods=['GET'])(GRAPH.graph)
APP.route('/graph/combine', methods=['GET'])(GRAPH.graph)
APP.route('/graph/selected', methods=['PUT'])(GRAPH_SELECTED.graph_selected)

# --------------------------------------------------------------
# REMOTE COMMAND
# --------------------------------------------------------------
RC_SYSTEM = rc_system.RCSystem()
REMOTE_COMMAND = remote_command.RemoteCommand()

# REMOTE COMMAND ROUTE
APP.route('/remote/command', methods=['POST'])(RC_SYSTEM.rc_system)
APP.route('/remote/command', methods=['GET'])(REMOTE_COMMAND.remote_command)

# --------------------------------------------------------------
# VPN
# --------------------------------------------------------------
VPN_DATA = vpn_data.VPNData()
VPN_UPDATE = vpn_update.VPNUpdate()

# VPN ROUTE
APP.route('/vpn/data', methods=['GET'])(VPN_DATA.vpn_data)
APP.route('/vpn/update', methods=['PUT'])(VPN_UPDATE.vpn_update)

# --------------------------------------------------------------
# DASHBOARD
# --------------------------------------------------------------
DASHBOARD = dashboard.Dashboard()

# DASHBOARD ROUTE
APP.route('/dashboard', methods=['GET'])(DASHBOARD.dashboard)

@APP.route('/')
@APP.route('/hello/')
def hello_world():
    """Hello World"""
    return 'Hello World!\n'


# --------------------------------------------------------------
# BLOCKAGE MAP
# --------------------------------------------------------------
BLOCKAGE = blockage.Blockage()

# BLOCKAGE ROUTE
APP.route('/blockage', methods=['GET'])(BLOCKAGE.blockage)


# --------------------------------------------------------------
# CATEGORY
# --------------------------------------------------------------
SUBCATEGORY = subcategory.SubCategory()
CREATE_SUBCATEGORY = create_subcategory.CreateSubCategory()
UPDATE_SUBCATEGORY = update_subcategory.UpdateSubCategory()
DELETE_SUBCATEGORY = delete_subcategory.DeleteSubCategory()
SUBCATEGORY_OPTION = subcategory_option.SubCategoryOption()


# CATEGORY ROUTE
APP.route('/subcategory', methods=['GET'])(SUBCATEGORY.subcategory)
APP.route('/subcategory/create', methods=['POST'])(CREATE_SUBCATEGORY.create_subcategory)
APP.route('/subcategory/update', methods=['PUT'])(UPDATE_SUBCATEGORY.update_subcategory)
APP.route('/subcategory/delete', methods=['DELETE'])(DELETE_SUBCATEGORY.delete_subcategory)
APP.route('/subcategory/options', methods=['POST'])(SUBCATEGORY_OPTION.subcategory_option)

# --------------------------------------------------------------
# VERSION
# --------------------------------------------------------------
VERSION = version.Version()
CREATE_VERSION = create_version.CreateVersion()
SET_VERSION = set_version.SetVersion()

# CATEGORY ROUTE
APP.route('/version', methods=['GET'])(VERSION.version)
APP.route('/version/create', methods=['POST'])(CREATE_VERSION.create_version)
APP.route('/version/set', methods=['POST'])(SET_VERSION.set_version)

# --------------------------------------------------------------
# CRON
# --------------------------------------------------------------
MONITORING = config_section_parser(CONFIG, "MONITORING")['enable']

if MONITORING.upper() == "TRUE":

    LOG.info("Cron will start in a while!")
    CRON = BackgroundScheduler()

    # EMAIL VESSEL INFO
    from controllers.cron import email_vessel_info
    EMAIL_VESSEL_INFO = email_vessel_info.EmailVesselInfo()

    # UPDATE VESSEL STATE
    from controllers.cron import cron_update_vessel_state
    CRON_UPDATE_VESSEL_STATE = cron_update_vessel_state.UpdateVesselState()

    # UPDATE DEVICE STATE
    from controllers.cron import update_device_state
    UPDATE_DEVICE_STATE = update_device_state.UpdateDeviceState()

    # UPDATE MODULE STATE
    from controllers.cron import update_module_state
    UPDATE_MODULE_STATE = update_module_state.UpdateModuleState()

    # UPDATE OPTION STATE
    from controllers.cron import update_option_state
    UPDATE_OPTION_STATE = update_option_state.UpdateOptionState()

    # UPDATE VESSELS INI FILE
    from controllers.cron import cron_update_inifiles
    CRON_UPDATE_INI_FILES = cron_update_inifiles.UpdateINIFiles()

    # VPN IP UPDATE
    from controllers.cron import vpn_ip_update
    VPN_IP_UPDATE = vpn_ip_update.VPNIPUpdate()

    # ALARM
    from controllers.cron import alarm_record
    ALARM_RECORD = alarm_record.AlarmRecord()

    # BLOCKAGE
    from controllers.cron import blockage_data
    BLOCKAGE_DATA = blockage_data.BlockageData()


    def goodbye():
        """Exit Cron"""
        CRON.shutdown()

    CRON.add_job(func=CRON_UPDATE_VESSEL_STATE.update_vessel_state, trigger="interval", minutes=1)
    CRON.add_job(func=EMAIL_VESSEL_INFO.email_vessel_info, trigger="interval", minutes=1)
    CRON.add_job(func=VPN_IP_UPDATE.vpn_ip_update, trigger="interval", minutes=10)

    CRON.add_job(func=UPDATE_DEVICE_STATE.update_device_state, trigger="interval", minutes=1)
    CRON.add_job(func=UPDATE_MODULE_STATE.update_module_state, trigger="interval", minutes=1)
    CRON.add_job(func=UPDATE_OPTION_STATE.update_option_state, trigger="interval", minutes=1)

    CRON.add_job(func=CRON_UPDATE_INI_FILES.update_ini_files, trigger="interval", minutes=5)

    # ALARM
    CRON.add_job(func=ALARM_RECORD.run, trigger="interval", minutes=1)
    CRON.add_job(func=BLOCKAGE_DATA.run, trigger="interval", minutes=1)
    CRON.add_job(func=ALARM_RECORD.run_current_alarm, trigger="interval", minutes=10)
    CRON.add_job(func=ALARM_RECORD.run_day_alarm, trigger="interval", minutes=10)

    # log.critical("No CRON running!!!")
    CRON.start()

    # Shutdown the CRON when exiting the APP
    # atexit.register(lambda: CRON.shutdown())
    atexit.register(goodbye)
# --------------------------------------------------------------


# --------------------------------------------------------------
# START
# --------------------------------------------------------------
if __name__ == '__main__':

    # server_type = config_section_parser(config, "SERVER")['server_type']

    # if server_type != 'production':
    #     APP.debug = True

    APP.run(host='0.0.0.0', port=8080)
