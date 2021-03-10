import os, sys, time, datetime
import pandas as pd
import numpy as np
import pyodbc
from itertools import zip_longest

from guided_LDA import GuidedLDA
from preprocess import module_catalogue_tokenizer, preprocess_keywords, preprocess_keyword, print_keywords


class Initialise_GuidedLDA_Model():

    def __progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __getDBTable(self, numOfModules):
        # SERVER LOGIN DETAILS
        server = 'miemie.database.windows.net'
        database = 'MainDB'
        username = 'miemie_login'
        password = 'e_Paswrd?!'
        driver = '{ODBC Driver 17 for SQL Server}'
        # CONNECT TO DATABASE
        myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

        if numOfModules == "MAX":
            df = pd.read_sql_query("SELECT Module_Name, Module_ID, Description FROM [dbo].[ModuleData]", myConnection)
            myConnection.commit()
            return df
        else:
            df = pd.read_sql_query("SELECT TOP (%d) Module_Name, Module_ID, Description FROM [dbo].[ModuleData]" % int(numOfModules), myConnection)
            myConnection.commit()
            return df

    def __moduleHasKeyword(self, data, df):
        indicies = []
        counter = 1
        length = len(data)

        for i in range(length):  # iterate through the paper descriptions
            self.__progress(counter, length, "processing for guidedLDA")
            moduleName = data["Module_Name"][i]
            if data["Description"][i]:
                description = data["Description"][i]
            else:
                description = ""
            textData = moduleName + " " + description

            text = module_catalogue_tokenizer(textData)
            for p in df:  # iterate through SDGs
                found = 0
                for j in df[p]: # iterate through the keyword in p SDG
                    temp = j
                    word = module_catalogue_tokenizer(j)
                    " ".join(text)
                    " ".join(word)
                    if word in text:
                        found += 1
                if found == 0:
                    indicies.append(i)
            counter += 1
        
        print()
        data.drop(indicies)
        return data

    def __moduleHasKeywordJSON(self, data):
        indicies = []
        dataJSON = pd.read_json('../MODULE_CATALOGUE/matchedModulesSDG.json')
        for p in dataJSON:
            listSDG = dataJSON[p]['Related_SDG']
            if len(listSDG) == 0:
                indicies.append(p)

        for i in indicies:
            data = data[data.Module_ID != i]
        return data

    def __load_dataset(self, numOfModules):
        df = pd.read_csv("../MODULE_CATALOGUE/SDG_KEYWORDS")
        df = df.dropna()
        data = self.__getDBTable(numOfModules)
        data = data.dropna()
        return pd.DataFrame(data=self.__moduleHasKeywordJSON(data), columns=["Module_ID", "Description"])

    def run(self):
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        keywords = preprocess_keywords("SDG_Keywords.csv")
        numberOfModules = "MAX"
        data = self.__load_dataset(numberOfModules)
        iterations = 400
        seed_confidence = 1.0

        lda = GuidedLDA(data, keywords, iterations)
        lda.train(seed_confidence)
        lda.display_document_topic_words(20)

        print("Size before/after filtering -->",  str(numberOfModules), "/", len(data))


Initialise_GuidedLDA_Model().run()