import time, datetime
import json
import numpy as np
import pymongo

import guidedlda

from NLP.GUIDED_LDA.guided_LDA import GuidedLda
from NLP.PREPROCESSING.preprocessor import Preprocessor
from LOADERS.publication_loader import PublicationLoader

class IheGuidedLda(GuidedLda):
    def __init__(self):
        self.loader = PublicationLoader()
        self.preprocessor = Preprocessor()
        self.data = None # scopus-publications dataframe with columns {DOI, Description}
        self.keywords = None # list of IHE-specific keywords
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 4, 1, 0.4)
        self.model = None

    def push_to_mongo(self, data):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.ModulePrediction
        key = value = data
        col.update_one(key, {"$set": value}, upsert=True)
        client.close()

    def run(self):
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        num_publications = "MAX"
        keywords = "IHE_KEYWORDS/ihe_keywords.csv"
        iterations = 400
        seed_confidence = 1.0
        num_top_words = 20

        pyldavis_html = "NLP/GUIDED_LDA/IHE_RESULTS/pyldavis.html"
        tsne_clusters_html = "NLP/GUIDED_LDA/IHE_RESULTS/tsne_clusters.html"
        model = "NLP/GUIDED_LDA/IHE_RESULTS/model.pkl"
        results = "NLP/GUIDED_LDA/IHE_RESULTS/training_results.json"
        
        self.load_dataset(num_publications)
        self.load_keywords(keywords)
        self.num_topics = len(self.keywords)

        print("Training...")
        self.train(seed_confidence, iterations)
        self.display_results(num_top_words, pyldavis_html, tsne_clusters_html)

        print("Saving results...")
        #self.write_results(num_top_words, results) # record current results.
        #self.serialize(model)