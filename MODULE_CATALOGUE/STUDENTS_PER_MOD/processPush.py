import datetime
import pyodbc
import requests
import sys, re, csv
from typing import Tuple

class UpdateStudentsPerModule():
    def __init__(self):
        # SERVER LOGIN DETAILS
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.curr_time = datetime.datetime.now()

        # CONNECT TO DATABASE
        self.myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server +
                                           ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)

    def __preProcess(self, text: str) -> Tuple[str, int, str]:
        """
            Cleans out text data, extract module name, module ID and number of students enrolled in the module
        """

        text = text.replace("\n", "").replace("\"", "").split("\t") # clean up the string, remove empty spaces and tabulation
        lastElem = text[len(text) - 1]

        try:
            numOfStudents = int(lastElem)
        except:
            numOfStudents = None
        text.remove(lastElem)
        assert(len(text) == 1)  # validate the text data

        moduleID = re.search("\((.*?)\)", text[0]).group().replace("(", "").replace(")", "") # extract the module ID using regex
        tempText = text[0].split(" ")
        assert(tempText[0].replace("(", "").replace(")", "") == moduleID)  # validate the moduleID data

        return text[0], numOfStudents, moduleID

    def __checkTableExists(self, tablename: str) -> bool:
        """
            Prior to pushing data on the MySQL database table, checks whether such table already exists
        """
        
        dbcur = self.myConnection.cursor()
        dbcur.execute("""SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

    def __checkIfExists(self, primaryKey: str) -> bool:
        """
            Check whether or not data for a particular module already exists in database table <ModuleID>
        """

        cur = self.myConnection.cursor()
        cur.execute("SELECT * FROM StudentsPerModule WHERE ModuleID = (?)", (primaryKey))
        data = cur.fetchall()
        if len(data) == 0:
            return False
        return True

    def __createTable(self) -> None:
        """
            Create MySQL database table <StudentsPerModule>
        """

        cur = self.myConnection.cursor()
        create = """CREATE TABLE StudentsPerModule(
                    ModuleID             VARCHAR(100) PRIMARY KEY,
                    NumberOfStudents     INT,
                    Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP);"""
        cur.execute(create)
        self.myConnection.commit()
        print("Created table <StudentsPerModule>")

    def __pushToDB(self, data: tuple) -> None:
        """
            Push a single module data to <StudentsPerModule> database table.
            Data has to retain integrity (3 elements in a tuple: str, int, timestamp)
        """

        cur = self.myConnection.cursor()
        if not data:
            print("Data error") # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
        else:
            # Eexecute insertion into the database table
            insertion = "INSERT INTO StudentsPerModule(ModuleID, NumberOfStudents, Last_Updated) VALUES (?, ?, ?)"
            cur.executemany(insertion, data)
        self.myConnection.commit()

    def update(self) -> None:
        """
            Controller method for self
            Creates database table if doesnt exist
            Reads initialised files, updates processed data to Azure SQL Server
        """

        # Making sure the table exists
        if not self.__checkTableExists("StudentsPerModule"):
            self.__createTable()

        counter = 0
        timestamp = datetime.datetime.now()
        with open("MODULE_CATALOGUE/STUDENTS_PER_MOD/studentsPerModule.csv", encoding='utf-16') as f:
            for i in f:
                data = [] # accumulator to store a tuple for pushing purposes
                counter += 1
                cleanText, numOfStudents, moduleID = self.__preProcess(i)
                data.append((moduleID, numOfStudents, timestamp))
                # Only push if no such record exists
                if not self.__checkIfExists(moduleID):
                    self.__pushToDB(data)
