import pyodbc

server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'

table_name = "test_table"

# CONNECT TO DATABASE
myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cur = myConnection.cursor()

# EXECUTE SQL COMMANDS
cur.execute("DROP TABLE IF EXISTS table_name;")
create = """CREATE TABLE table_name(
    Test_ID            VARCHAR(50),
    Last_Updated    DATETIME DEFAULT CURRENT_TIMESTAMP
);"""
cur.execute(create)
myConnection.commit()
print("Successully created table:", table_name)
