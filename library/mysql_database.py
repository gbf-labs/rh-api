# # pylint: disable=attribute-defined-outside-init, superfluous-parens
# """MySQL Database"""
# import ConfigParser
# import MySQLdb as my
# from library.config_parser import config_section_parser

# class MySQLDatabase():
#     """Class for MySQLDatabase"""
#     # SET ALL THE WEB DATABASE CONFIG
#     def __init__(self):
#         """The Constructor for MySQLDatabase class"""
#         # INIT CONFIG
#         self.config = ConfigParser.ConfigParser()
#         # CONFIG FILE
#         self.config.read("config/config.cfg")

#         # SET CONFIG VALUES
#         self.host = config_section_parser(self.config, "MYSQL")['host']
#         self.database = config_section_parser(self.config, "MYSQL")['database']
#         self.username = config_section_parser(self.config, "MYSQL")['user']
#         self.password = config_section_parser(self.config, "MYSQL")['password']

#     # CONNECTION TO DATABASE WITH DATABASE NAME
#     def open_connection(self):
#         """Open Connection"""
#         # SET CONNECTION
#         connection_result = my.connect(host=self.host, user=self.username,
#                                        passwd=self.password, db=self.database)

#         # CONNECTION RESULT
#         self.cursor = connection_result.cursor()
#         self.db = connection_result

#     # CONNECTION TO DATABASE W OR W/O DATABASE NAME
#     def connection_to_db(self, db=None):
#         """Connection to Database with or Without Database Name"""
#         # CHECK db
#         if db is None:

#             # SET CONNECTION
#             connection_result = my.connect(host=self.host,
#                                            user=self.username,
#                                            passwd=self.password)

#             # CONNECTION RESULT
#             self.cursor = connection_result.cursor()
#             self.db = connection_result

#         else:

#             # SET CONNECTION
#             connection_result = my.connect(host=self.host,
#                                            user=self.username,
#                                            passwd=self.password,
#                                            db=db)

#             # CONNECTION RESULT
#             self.cursor = connection_result.cursor()
#             self.db = connection_result

#     # FETCH ONE RETURN JSON DATA
#     def query_fetch_one(self, sql_string):
#         """Fetch one return JSON Data"""
#         # QUERY EXECUTE
#         self.cursor.execute(sql_string)

#         # GET ALL HEADERS
#         row_headers = [x[0] for x in self.cursor.description]

#         # FETCH ONE DATA
#         result = self.cursor.fetchone()

#         # CONDITION FOR THE RESULT
#         if result:

#             # SET RESULT TO JSON
#             data = (dict(zip(row_headers, result)))

#             # RETURN
#             return data

#         # RETURN
#         return 0

#     # FETCH ALL DATA DEPEND ON QUERY AND RETURN JSON DATA
#     def query_fetch_all(self, sql_string):
#         """Fetch All Data"""
#         # QUERY EXECUTE
#         self.cursor.execute(sql_string)

#         # GET ALL HEADERS
#         row_headers = [x[0] for x in self.cursor.description]

#         # FETCH ALL DATA
#         query_result = self.cursor.fetchall()

#         # CONDITION FOR THE RESULT
#         if query_result:

#             # INIT VARIABLE
#             data = []

#             # LOOP DATA
#             for row in query_result:
#                 # SET RESULT TO JSON
#                 data.append(dict(zip(row_headers, row)))

#             # RETURN
#             return data

#         # RETURN
#         return 0

#     # COMMIT QUERY
#     def query_commit(self, sql_string):
#         """Query Commit"""
#         # QUERY EXECUTE
#         self.cursor.execute(sql_string)

#         # COMMIT
#         self.db.commit()

#     # DATABASES QUERY
#     def query_dbs(self, sql_string):
#         """Query DBs"""
#         # INIT VARIABLES
#         dbs = []

#         # QUERY EXECUTE
#         self.cursor.execute(sql_string)

#         # LOOP DATABASES
#         for (databases) in self.cursor:

#             # APPEND TO VARIBALE
#             dbs.append(databases[0])

#         # RETURN
#         return dbs

#     # CLOSE CONNECTION TO DATABASE
#     def close_connection(self):
#         """Close Connection"""
#         # CLOSE CONNECTION
#         self.cursor.close()
