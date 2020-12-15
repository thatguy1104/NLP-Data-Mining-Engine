import pandas as pd
import pyodbc


class NLP():
    def __init__(self):
        # SERVER LOGIN DETAILS
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'

    def get_data(self):
        # CONNECT TO DATABASE
        myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        cur = myConnection.cursor()

        # Query into dataframe
        df = pd.read_sql_query("""SELECT TOP (5) * FROM [dbo].[ModuleData]""", myConnection)

        print(df)

        myConnection.commit()
        myConnection.close()



obj = NLP()
obj.get_data()