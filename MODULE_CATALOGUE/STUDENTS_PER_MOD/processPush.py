import datetime
import pyodbc
import requests
import sys, re, csv


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

    def preProcess(self, text):
        text = text.replace("\n", "").replace("\"", "").split("\t")
        lastElem = text[len(text) - 1]
        try:
            numOfStudents = int(lastElem)
        except:
            numOfStudents = None
        text.remove(lastElem)
        assert(len(text) == 1)  # validate the text data

        moduleID = re.search("\((.*?)\)", text[0]).group().replace("(", "").replace(")", "")
        tempText = text[0].split(" ")
        assert(tempText[0].replace("(", "").replace(")", "") == moduleID)  # validate the moduleID data

        return text[0], numOfStudents, moduleID

    def checkTableExists(self, tablename):
        dbcur = self.myConnection.cursor()
        dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

    def checkIfExists(self, primaryKey):
        cur = self.myConnection.cursor()
        cur.execute("SELECT * FROM StudentsPerModule WHERE ModuleID = (?)", (primaryKey))
        data = cur.fetchall()
        if len(data) == 0:
            return False
        return True

    def createTable(self):
        cur = self.myConnection.cursor()
        create = """CREATE TABLE StudentsPerModule(
                    ModuleID             VARCHAR(100) PRIMARY KEY,
                    NumberOfStudents     INT,
                    Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP);"""
        cur.execute(create)
        self.myConnection.commit()
        print("Created table <StudentsPerModule>")

    def pushToDB(self, data):
        cur = self.myConnection.cursor()
        # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
        if not data:
            print("Data error")
        else:
            # EXECUTE INSERTION INTO DB
            insertion = "INSERT INTO StudentsPerModule(ModuleID, NumberOfStudents, Last_Updated) VALUES (?, ?, ?)"
            cur.executemany(insertion, data)
        self.myConnection.commit()

    def update(self):
        if not self.checkTableExists("StudentsPerModule"):
            self.createTable()

        counter = 0
        timestamp = datetime.datetime.now()
        with open("MODULE_CATALOGUE/STUDENTS_PER_MOD/studentsPerModule.csv", encoding='utf-16') as f:
            for i in f:
                data = []
                counter += 1
                cleanText, numOfStudents, moduleID = self.preProcess(i)
                data.append((moduleID, numOfStudents, timestamp))
                if not self.checkIfExists(moduleID):
                    self.pushToDB(data)
