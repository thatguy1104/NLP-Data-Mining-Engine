import os, sys, re
import json
import pandas as pd
import pymongo

from LOADERS.publication_loader import PublicationLoader
from MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from NLP.PREPROCESSING.preprocessor import Preprocessor

class ScopusStringMatch():
    def __init__(self):
        self.loader = PublicationLoader()
        self.mongodb_pusher = MongoDbPusher()
        self.preprocessor = Preprocessor()

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
        num_publications = len(data)
        num_keywords = len(keywords)
        
        for doi, publication in data.items():
            self.progress(counter, num_publications, "processing scopus_matches.json")
            counter += 1
            description = self.preprocessor.tokenize(publication["Description"])
        
            sdg_occurences = {}
            for n in range(num_keywords):
                sdg_num = n + 1
                sdg = "SDG " + str(sdg_num) if sdg_num < num_keywords else "Misc"
                sdg_occurences[sdg] = {"Word_Found": []}
                for keyword in keywords[n]:
                    if keyword in description:
                        sdg_occurences[sdg]["Word_Found"].append(keyword)
                if len(sdg_occurences[sdg]["Word_Found"]) == 0:
                    sdg_occurences.pop(sdg, None)

                resulting_data[doi] = {"PublicationInfo" : publication, "Related_SDG" : sdg_occurences}

        self.mongodb_pusher.matched_scopus(resulting_data)
        print()
        with open('NLP/STRING_MATCH/SDG_RESULTS/scopus_matches.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
        
    def run(self):
        data = self.loader.load_all()
        self.read_keywords(data)
