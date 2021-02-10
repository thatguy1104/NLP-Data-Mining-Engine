import os, sys, re
import json
import pyodbc
import datetime
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

numberOfModulesAnalysed = "MAX"

class ModuleMap():
    
    def __init__(self):
        # SERVER LOGIN DETAILS
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.curr_time = datetime.datetime.now()

        # CONNECT TO DATABASE
        self.myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server +';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def preprocessText(self, text):
        # Normalisation
        # replace UCL module codes.
        normalized = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text)
        normalized = re.sub(r'[/]', " ", normalized)  # separate forward slashes
        # replace numbers.
        normalized = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', normalized)
        normalized = re.sub("[^\w]", " ", normalized)  # remove punctuation.

        # Tokenisation
        tokens = word_tokenize(normalized.lower())
        n = len(tokens)

        # Stopword Removal
        stops = set(stopwords.words('english'))
        tokens = [word for word in tokens if not word in stops]

        # Lemmatising and Stemming
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]

        return " ".join(tokens)

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
            df = pd.read_sql_query("SELECT TOP (%d) * FROM [dbo].[ModuleData]" % int(numberOfModulesAnalysed), self.myConnection)
            self.myConnection.commit()
            return df

    def readKeywords(self,data):
        fileName = "SDG_Keywords.csv"
        # SDG keyword data
        df = pd.read_csv(fileName)
        df = df.dropna()
        resulting_data = {}
        counter = 0
        length = len(data)

        # # Reset the data file
        if os.path.exists("MODULE_CATALOGUE/matchedModulesSDG.json"):
            os.remove("MODULE_CATALOGUE/matchedModulesSDG.json")

        occuringWordCount = {}
        for p in df:  # iterate through SDGs
            occuringWordCount[p] = {}
            for j in df[p]:
                occuringWordCount[p][j] = 0

        for i in range(length):  # iterate through the paper descriptions
            self.progress(counter, length, "processing MODULE_CATALOGUE/matchedModulesSDG.json")
            counter += 1
            moduleName = data["Module_Name"][i]
            if data["Description"][i]:
                description = data["Description"][i]
            else:
                description = ""
            textData = moduleName + " " + description

            sdg_occurences = {}
            for p in df:  # iterate through SDGs
                sdg_occurences[p] = {"Word_Found": []}
                for j in df[p]: # iterate through the keyword in p SDG
                    temp = j
                    text = self.preprocessText(textData)
                    word = self.preprocessText(j)
                    if word in text:
                        occuringWordCount[p][temp] += 1
                        sdg_occurences[p]["Word_Found"].append(j)
                if len(sdg_occurences[p]["Word_Found"]) == 0:
                    del sdg_occurences[p]
                resulting_data[data["Module_ID"][i]] = {"Module_Name": data["Module_Name"][i], "Related_SDG": sdg_occurences}
        print()
        with open('MODULE_CATALOGUE/matchedModulesSDG.json', 'a') as outfile:
            json.dump(resulting_data, outfile)
        with open('MODULE_CATALOGUE/sdgCount.json', 'w') as outfile:
            json.dump(occuringWordCount, outfile)
    
    def run(self):
        data = self.getFileData()
        self.readKeywords(data)

