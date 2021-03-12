import os, sys, time, datetime
import pandas as pd
import numpy as np
import pyodbc
import pickle
from itertools import zip_longest
from NLP.LDA.LDA import LDA
from NLP.preprocess import module_catalogue_tokenizer, preprocess_keyword, preprocess_keywords, print_keywords


class Initialise_LDA_Model():

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

    def __preprocess_keywords_example(self):
        seed_topic_list = [['fruit', 'food', 'banana', 'apple juice', 'apple'],
                            ['sport', 'football', 'basketball', 'bowling'],
                            ['ocean', 'fish']]
        for i in range(len(seed_topic_list)):
            seed_topic_list[i] = [' '.join(module_catalogue_tokenizer(w)) for w in seed_topic_list[i]]
        return seed_topic_list

    def __load_dataset_example(self):
        data = [
            "I like fruit such as banana, apple and orange.", # food
            "The football match was a great game! I like the sports football, basketball and cricket.", # sports
            "This morning I made a smoothie with banana, apple juice and kiwi.", # food
            "The ocean is warm and the fish were swimming. I want to go snorkeling tomorrow and play football on the beach" # ocean
        ]
        return pd.DataFrame(data=data, columns=["Description"])

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
        dataJSON = pd.read_json('MODULE_CATALOGUE/matchedModulesSDG.json')

        for p in dataJSON:
            listSDG = dataJSON[p]['Related_SDG']
            if len(listSDG) == 0:
                indicies.append(p)

        for i in indicies:
            data = data[data.Module_ID != i]
        return data

    def __load_dataset(self, numOfModules):
        df = pd.read_csv("MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv")
        df = df.dropna()
        data = self.__getDBTable(numOfModules)
        data = data.dropna()

        return pd.DataFrame(data=data, columns=["Module_ID", "Description"])

    def __run_example(self):
        keywords = self.preprocess_keywords_example()
        data = self.__load_dataset_example()
        n_passes = 100
        n_iterations = 400

        lda = LDA(data, keywords)
        lda.train(n_passes, n_iterations, 10)

    def __serializeLDA(self, filename, lda):
        filename = filename + ".pkl"
        with open(filename, 'wb') as f:
            pickle.dump(lda, f)

    def create(self):
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        keywords = preprocess_keywords("MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv")
        numberOfModules = "MAX"
        
        print("Loading dataset...")
        data = self.__load_dataset(numberOfModules)

        print("Size before/after filtering -->",  str(numberOfModules), "/", len(data))
        n_passes = 10
        n_iterations = 400

        print("Training...")
        lda = LDA(data, keywords)
        lda.train(n_passes, n_iterations, 20)
        
        self.__serializeLDA("NLP/LDA/lda_model", lda)
