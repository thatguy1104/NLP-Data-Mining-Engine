import os, sys, re
import json
import pandas as pd
import pymongo

from main.LOADERS.publication_loader import PublicationLoader
from main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from main.NLP.PREPROCESSING.preprocessor import Preprocessor


class ScopusStringMatch_SDG():
    
    def __init__(self):
        self.loader = PublicationLoader()
        self.mongodb_pusher = MongoDbPusher()
        self.preprocessor = Preprocessor()

    def __progress(self, count, total, custom_text, suffix=''):
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __read_keywords(self, data: dict) -> None:
        """
            Given a set of publications in a dictionary, performs pre-processing for all string type data fields.
            Performs look-up on SDG keyword occurences in a document.
            Results are pushed to MongoDB (backed-up in JSON file - scopus_matches.json).
        """

        resulting_data = {}
        counter = 0
        keywords = self.preprocessor.preprocess_keywords("main/SDG_KEYWORDS/SDG_Keywords.csv")
        num_publications = len(data)
        num_keywords = len(keywords)

        for doi, publication in data.items():
            # visualise the progress on a commandline
            self.__progress(counter, num_publications, "processing scopus_matches.json")
            counter += 1
            description = self.preprocessor.tokenize(publication["Description"]) 
            sdg_occurences = {} # accumulator for SDG Keywords found in a given document
            for n in range(num_keywords):
                sdg_num = n + 1
                sdg = "SDG " + str(sdg_num) if sdg_num < num_keywords else "Misc" # clean and process the string for documenting occurences
                sdg_occurences[sdg] = {"Word_Found": []}
                for keyword in keywords[n]:
                    if keyword in description:
                        sdg_occurences[sdg]["Word_Found"].append(keyword)
                if len(sdg_occurences[sdg]["Word_Found"]) == 0:
                    sdg_occurences.pop(sdg, None) # clear out empty occurences

                resulting_data[doi] = {"DOI": doi, "Related_SDG": sdg_occurences}
        print()
        self.mongodb_pusher.matched_scopus(resulting_data) # push the processed data to MongoDB
        print()
        # Record the same data locally, acts as a backup
        with open('main/NLP/STRING_MATCH/SDG_RESULTS/scopus_matches.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
        
    def run(self):
        """
            Controller method for self class
            Loads modules from a pre-loaded pickle file
        """

        data = self.loader.load_all()
        self.__read_keywords(data)
