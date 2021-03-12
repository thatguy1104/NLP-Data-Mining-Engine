import pandas as pd
import pyodbc
from bson import json_util
from LOADERS.loader import Loader

class ModuleLoader(Loader):
    def get_module_db_table(self, num_modules):
        # SERVER LOGIN DETAILS
        server = 'miemie.database.windows.net'
        database = 'MainDB'
        username = 'miemie_login'
        password = 'e_Paswrd?!'
        driver = '{ODBC Driver 17 for SQL Server}'
        # CONNECT TO DATABASE
        myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

        if num_modules == "MAX":
            df = pd.read_sql_query("SELECT Module_Name, Module_ID, Description FROM [dbo].[ModuleData]", myConnection)
        else:
            df = pd.read_sql_query("SELECT TOP (%d) Module_Name, Module_ID, Description FROM [dbo].[ModuleData]" % int(num_modules), myConnection)

        myConnection.commit()
        return df

    def load(self, num_modules):
        data = self.get_db_table(num_modules)
        data = data.dropna()
        return pd.DataFrame(data=data, columns=["Module_ID", "Description"])