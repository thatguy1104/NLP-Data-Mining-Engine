import pyodbc

server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'

myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cur = myConnection.cursor()

create = """CREATE TABLE ModuleData(
                Department_Name      VARCHAR(150),
                Department_ID        VARCHAR(150),
                Module_Name          VARCHAR(150),
                Module_ID            VARCHAR(150) PRIMARY KEY,
                Faculty              VARCHAR(100),
                Credit_Value         FLOAT,
                Module_Lead          VARCHAR(100),
                Catalogue_Link       VARCHAR(MAX),
                Description          VARCHAR(MAX),
                Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""

cur.execute(create)
myConnection.commit()
myConnection.close()
