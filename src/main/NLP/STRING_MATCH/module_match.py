import os, sys, re
import json
import pyodbc
import datetime
import pandas as pd
import pymongo

from main.LOADERS.module_loader import ModuleLoader
from main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from main.NLP.PREPROCESSING.module_preprocessor import ModuleCataloguePreprocessor

class ModuleStringMatch():
    def __init__(self):
        self.loader = ModuleLoader()
        self.mongodb_pusher = MongoDbPusher()
        self.preprocessor = ModuleCataloguePreprocessor()

    def __progress(self, count: int, total: int, custom_text: str, suffix: str ='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __read_keywords(self, data: pd.DataFrame) -> None:
        """
            Given a set of module data in a Pandas DataFrame (columns=[Module_Name, Module_ID, Description]), performs pre-processing for all string type data fields.
            Performs look-up on SDG keyword occurences in a document.
            Results are pushed to MongoDB (backed-up in JSON file - scopus_matches.json).
        """
    
        resulting_data = {}
        counter = 0
        keywords = self.preprocessor.preprocess_keywords("main/SDG_KEYWORDS/SDG_Keywords.csv")
        stopwords = self.preprocessor.stopwords
        num_modules = len(data)
        num_keywords = len(keywords)

        # Iterate through the module descriptions.
        for i in range(num_modules):
            self.__progress(counter, len(data), "processing module_matches.json") # visualise the progress on a commandline
            counter += 1
            
            module_name = data["Module_Name"][i]
            module_description = ""
            # Descriptions for some modules are absent, checker statement is needed
            if data["Module_Description"][i]:
                module_description = data["Module_Description"][i]

            module_text = module_name + " " + module_description
            module_text = " ".join(self.preprocessor.tokenize(module_text)) # preprocess module text.

            sdg_occurences = {}
            for n in range(num_keywords):
                sdg_num = n + 1
                sdg = "SDG " + str(sdg_num) if sdg_num < num_keywords else "Misc" # clean and process the string for documenting occurences
                sdg_occurences[sdg] = {"Word_Found": []}
                for keyword in keywords[n]:
                    if keyword in module_text and keyword not in stopwords:
                        sdg_occurences[sdg]["Word_Found"].append(keyword)
                
                if len(sdg_occurences[sdg]["Word_Found"]) == 0:
                    del sdg_occurences[sdg]  # clear out empty occurences
                
                resulting_data[data["Module_ID"][i]] = {"Module_Name": data["Module_Name"][i], "Related_SDG": sdg_occurences}
        
        self.mongodb_pusher.matched_modules(resulting_data) # push the processed data to MongoDB
        print()
        # Record the same data locally, acts as a backup
        with open('main/NLP/STRING_MATCH/SDG_RESULTS/module_matches.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
    
    def run(self) -> None:
        """
            Controller method for self class.
            Loads modules from a pre-loaded pickle file.
            MAX (default parameter) specifies number of modules to load.
        """
        data = self.loader.get_modules_db("MAX")
        self.__read_keywords(data)
