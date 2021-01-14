import pyodbc

server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'

myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cur = myConnection.cursor()

create = """CREATE TABLE ModuleKeywords(
                Module_ID            VARCHAR(150) PRIMARY KEY,
                Keyword_1            VARCHAR(200),
                Frequency_1          FLOAT,
                Keyword_2            VARCHAR(200),
                Frequency_2          FLOAT,
                Keyword_3            VARCHAR(200),
                Frequency_3          FLOAT,
                Keyword_4            VARCHAR(200),
                Frequency_4          FLOAT,
                Keyword_5            VARCHAR(200),
                Frequency_5          FLOAT,
                Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""

cur.execute(create)
myConnection.commit()
myConnection.close()