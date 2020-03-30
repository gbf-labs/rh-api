# #====================================#
# # AUTHOR:      KRISFEN DUCAO         #
# #====================================#
# # pylint: disable=too-few-public-methods
# """DB Index"""
# # from flask import  jsonify, request
# from library.MySQLDatabase import MySQLDatabase
# from library.common import Common

# class DBIndex(Common, MySQLDatabase):
#     """Class for DBIndex"""

#     def index(self):
#         """Return DB Index"""

#         # return None

#         # CONNECT TO DATABASE
#         self.open_connection()

#         # INCREASE THE BUFFER SIZE IN MYSQL
#         sql_str = "SET @newsize = 1024 * 1024 * 256"
#         self.query_commit(sql_str)

#         sql_str = "SET GLOBAL key_buffer_size = @newsize;"
#         self.query_commit(sql_str)

#         # CLOSE DB CONNECTION
#         self.close_connection()

#         # RETURN
#         return 1
