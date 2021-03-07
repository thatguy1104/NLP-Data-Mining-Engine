import pyodbc

server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'

myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server +
                              ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cur = myConnection.cursor()

create = """CREATE TABLE ModuleMappings(
                Module_ID             VARCHAR(150) PRIMARY KEY,
                SDG_1                 INT,
                SDG_2                 INT,
                SDG_3                 INT,
                SDG_4                 INT,
                SDG_5                 INT,
                SDG_6                 INT,
                SDG_7                 INT,
                SDG_8                 INT,
                SDG_9                 INT,
                SDG_10                 INT,
                SDG_11                 INT,
                SDG_12                 INT,
                SDG_13                 INT,
                SDG_14                 INT,
                SDG_15                 INT,
                SDG_16                 INT,
                SDG_17                 INT,
                Misc                  INT,
                Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""

cur.execute(create)
myConnection.commit()
myConnection.close()
