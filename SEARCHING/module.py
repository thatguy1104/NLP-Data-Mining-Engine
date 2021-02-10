import pyodbc
import pandas as pd
from search_algo import RabinKarp

numberOfModulesAnalysed = 10


class ScopusSearch():

    def __init__(self):
        # SERVER LOGIN DETAILS
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'

        # CONNECT TO DATABASE
        self.myConnection = pyodbc.connect(
            'DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)

    def getFileData(self):
        cur = self.myConnection.cursor()
        numberModules = 1
        if numberOfModulesAnalysed == "MAX":
            # Query into dataframe
            df = pd.read_sql_query("SELECT * FROM [dbo].[ModuleData]", self.myConnection)
            self.myConnection.commit()
            return df
        else:
            # Query into dataframe
            df = pd.read_sql_query("SELECT TOP (%d) * FROM [dbo].[ModuleData]" % int(numberOfModulesAnalysed),
                                   self.myConnection)
            self.myConnection.commit()
            return df

    def getKeywords(self):
        fileName = "../sample_keywords.csv"
        df = pd.read_csv(fileName, header=None)
        return df

    def process(self):
        data = self.getFileData()        
        keywords = self.getKeywords().values.tolist()[0]
        len_data = len(data)
        len_words = len(keywords)
        searchAlgorithm = RabinKarp()
        
        for i in range(len_data):
            for j in range(len_words):
                print(data["Module_ID"][i], keywords[j])
                searchAlgorithm.search(data["Description"][i], keywords[j])
            print()


obj = ScopusSearch()
obj.process()
