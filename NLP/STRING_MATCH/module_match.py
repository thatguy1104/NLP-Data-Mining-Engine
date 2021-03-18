import os, sys, re
import json
import pyodbc
import datetime
import pandas as pd
import pymongo

from LOADERS.module_loader import ModuleLoader
from MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from NLP.PREPROCESSING.module_preprocessor import ModuleCataloguePreprocessor

class ModuleStringMatch():
    def __init__(self):
        self.loader = ModuleLoader()
        self.mongodb_pusher = MongoDbPusher()
        self.preprocessor = ModuleCataloguePreprocessor()

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def read_keywords(self, data):
        resulting_data = {}
        counter = 0
        keywords = self.preprocessor.preprocess_keywords("SDG_KEYWORDS/SDG_Keywords.csv")
        stopwords = self.preprocessor.stopwords
        num_modules = len(data)
        num_keywords = len(keywords)

        # Iterate through the module descriptions.
        for i in range(num_modules):
            self.progress(counter, len(data), "processing module_matches.json")
            counter += 1
            
            module_name = data["Module_Name"][i]
            module_description = ""
            if data["Description"][i]:
                module_description = data["Description"][i]

            module_text = module_name + " " + module_description
            module_text = " ".join(self.preprocessor.tokenize(module_text)) # preprocess module text.

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
        
        self.mongodb_pusher.matched_modules(resulting_data)
        print()
        with open('NLP/STRING_MATCH/SDG_RESULTS/module_matches.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
    
    def run(self):
        data = self.loader.get_modules_db("MAX")
        self.read_keywords(data)