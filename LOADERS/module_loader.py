import pandas as pd
import pyodbc
import pickle
from bson import json_util
from LOADERS.loader import Loader

class ModuleLoader(Loader):
    def __init__(self):
        self.data_file = "LOADERS/modules.pkl"

    def get_modules_db(self, num_modules):
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

    def load(self, count):
        with open(self.data_file, "rb") as input_file:
            data = pickle.load(input_file)
        data = data.dropna()
        data = data.head(count) if isinstance(count, int) else data
        return pd.DataFrame(data=data, columns=["Module_ID", "Description"])

    def load_pymongo_db(self):
        print("Loading modules from SQL server...")
        data = self.get_modules_db("MAX")
        with open(self.data_file, "wb") as output_file:
            pickle.dump(data, output_file)