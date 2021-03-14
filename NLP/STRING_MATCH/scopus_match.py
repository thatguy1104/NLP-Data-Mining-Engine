import os, sys, re
import json
import pandas as pd
import pymongo

from NLP.PREPROCESSING.preprocessor import Preprocessor
from LOADERS.publication_loader import PublicationLoader

client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.Scopus
col = db.MatchedScopus

class ScopusStringMatch():

    def __init__(self):
        self.loader = PublicationLoader()
        self.preprocessor = Preprocessor()

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    '''
    def load_publications(self):
        resulting_data = {}
        data = PublicationLoader().load()
        
        for i in data:
            i = json.loads(json_util.dumps(i))
            del i['_id']
            resulting_data[i["DOI"]] = i
        return resulting_data
    '''

    def __pushToMongoDB(self, data):
        for i in data:
            value = data[i]
            col.update_one({"DOI": data[i]["DOI"]}, {"$set": value}, upsert=True)

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
            
        self.__pushToMongoDB(resulting_data)
        print()
        client.close()
        with open('NLP/STRING_MATCH/SDG_RESULTS/scopus_matches.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
        
    def run(self):
        data = self.loader.load()
        self.read_keywords(data)
