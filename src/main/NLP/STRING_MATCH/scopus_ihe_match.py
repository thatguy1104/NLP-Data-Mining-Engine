import os
import sys
import re
import json
import pandas as pd
import pymongo

from main.LOADERS.publication_loader import PublicationLoader
from main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from main.NLP.PREPROCESSING.preprocessor import Preprocessor


class ScopusStringMatch_IHE():

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
        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __read_keywords(self, data: dict) -> None:
        """
            Given a set of publications in a dictionary, performs pre-processing for all string type data fields.
            Performs look-up on IHE keyword occurences in a document.
            Results are pushed to MongoDB (backed-up in JSON file - scopus_ihe_matches.json).
        """

        resulting_data = {}
        counter = 0
        keywords = self.preprocessor.preprocess_keywords("main/IHE_KEYWORDS/stringmatch_specialities.csv")
        num_publications, num_keywords = len(data), len(keywords)
    
        for doi, publication in data.items():
            self.__progress(counter, num_publications,"processing scopus_ihe_matches.json")
            
            # visualise the progress on a commandline
            description = ' '.join(self.preprocessor.tokenize(publication["Description"]))
            ihe_occurences = {}  # accumulator for SDG Keywords found in a given document
            for n in range(num_keywords):
                ihe_num = n + 1
                # clean and process the string for documenting occurences
                ihe = "IHE " + str(ihe_num)
                ihe_occurences[ihe] = []
                for keyword in keywords[n]:
                    if re.search(r'\b{0}\b'.format(keyword), description):
                        ihe_occurences[ihe].append(keyword)
                if len(ihe_occurences[ihe]) == 0:
                    ihe_occurences.pop(ihe, None)  # clear out empty occurences

                resulting_data[doi] = ihe_occurences
            counter += 1
        print()
        # push the processed data to MongoDB
        # self.mongodb_pusher.matched_scopus(resulting_data)
        print()
        # Record the same data locally, acts as a backup
        with open('main/NLP/STRING_MATCH/IHE_RESULTS/scopus_ihe_matches.json', 'w') as outfile:
            json.dump(resulting_data, outfile)

    def run(self):
        """
            Controller method for self class
            Loads modules from a pre-loaded pickle file
        """
        print("Loading publications...")
        data = self.loader.load_all()
        # data = self.loader.load_all_limit(20)
        print("Loaded publications")
        self.__read_keywords(data)


