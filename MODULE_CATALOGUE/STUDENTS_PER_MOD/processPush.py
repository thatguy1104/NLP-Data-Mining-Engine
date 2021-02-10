import datetime
import pyodbc
import requests
import sys, re, csv


# SERVER LOGIN DETAILS
server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'
curr_time = datetime.datetime.now()

# CONNECT TO DATABASE
myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)


def preProcess(text):
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

def checkTableExists(tablename):
    dbcur = myConnection.cursor()
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

def checkIfExists(primaryKey):
        cur = myConnection.cursor()
        cur.execute("SELECT * FROM StudentsPerModule WHERE ModuleID = (?)", (primaryKey))
        data = cur.fetchall()
        if len(data) == 0:
            return False
        return True

def createTable():
    cur = myConnection.cursor()
    create = """CREATE TABLE StudentsPerModule(
                ModuleID             VARCHAR(100) PRIMARY KEY,
                NumberOfStudents     INT,
                Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP);"""
    cur.execute(create)
    myConnection.commit()
    print("Created table <StudentsPerModule>")

def pushToDB(data):
    cur = myConnection.cursor()
    # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
    if not data:
        print("Data error")
    else:
        # EXECUTE INSERTION INTO DB
        insertion = "INSERT INTO StudentsPerModule(ModuleID, NumberOfStudents, Last_Updated) VALUES (?, ?, ?)"
        cur.executemany(insertion, data)
    myConnection.commit()

def run():
    if not checkTableExists("StudentsPerModule"):
        createTable()

    counter = 0
    timestamp = datetime.datetime.now()
    with open("studentsPerModule.csv", encoding='utf-16') as f:
        for i in f:
            data = []
            counter += 1
            cleanText, numOfStudents, moduleID = preProcess(i)
            data.append((moduleID, numOfStudents, timestamp))
            if not checkIfExists(moduleID):
                pushToDB(data)
            print("Processing", counter)

run()