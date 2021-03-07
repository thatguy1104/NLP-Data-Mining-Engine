import os, sys, re
import json
import pyodbc
import datetime
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from NLP.LDA.LDA_map import preprocess_keywords, preprocess_keyword
from NLP.preprocess import module_catalogue_tokenizer, get_stopwords


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

    def get_file_data(self):
        cur = self.myConnection.cursor()
        numberModules = 1
        if numberOfModulesAnalysed == "MAX":
            # Query into dataframe.
            df = pd.read_sql_query("SELECT * FROM [dbo].[ModuleData]", self.myConnection)
            self.myConnection.commit()
            return df
        else:
            # Query into dataframe.
            df = pd.read_sql_query("SELECT TOP (%d) * FROM [dbo].[ModuleData]" % int(numberOfModulesAnalysed), self.myConnection)
            self.myConnection.commit()
            return df

    def read_keywords(self, data):
        resulting_data = {}
        counter = 0
        keywords = preprocess_keywords("MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv")
        stopwords = get_stopwords()
        num_modules = len(data)
        num_keywords = len(keywords)

        # Reset the data file.
        # if os.path.exists("MODULE_CATALOGUE/matchedModulesSDG.json"):
        #     os.remove("MODULE_CATALOGUE/matchedModulesSDG.json")

        # Iterate through the module descriptions.
        for i in range(num_modules):
            self.progress(counter, len(data), "processing MODULE_CATALOGUE/matchedModulesSDG.json")
            counter += 1
            
            module_name = data["Module_Name"][i]
            module_description = ""
            if data["Description"][i]:
                module_description = data["Description"][i]

            module_text = module_name + " " + module_description
            module_text = " ".join(module_catalogue_tokenizer(module_text)) # preprocess module text.

            sdg_occurences = {}
            for n in range(num_keywords):
                sdg_num = n + 1
                sdg = "SDG " + str(sdg_num) if sdg_num < num_keywords else "Misc"
                sdg_occurences[sdg] = {"Word_Found": []}
                for keyword in keywords[n]:
                    if keyword in module_text and keyword not in stopwords:
                        sdg_occurences[sdg]["Word_Found"].append(keyword)
                
                if len(sdg_occurences[sdg]["Word_Found"]) == 0:
                    del sdg_occurences[sdg]
                
                resulting_data[data["Module_ID"][i]] = {"Module_Name": data["Module_Name"][i], "Related_SDG": sdg_occurences}

        print()
        with open('MODULE_CATALOGUE/matchedModulesSDG.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
    
    def run(self):
        data = self.get_file_data()
        self.read_keywords(data)
