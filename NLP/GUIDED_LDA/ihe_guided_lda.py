import time, datetime
import json
import numpy as np
import pymongo
import ssl

from LIBRARIES.GuidedLDA import guidedlda

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
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        #col = db.IHEPrediction
        # col.drop()
        #key = value = data
        #col.update_one(key, {"$set": value}, upsert=True)
        client.close()

    def display_document_topics(self):
        doc_topic = self.model.doc_topic_
        documents = self.data.DOI
        for doc, doc_topics in zip(documents, doc_topic):
            doc_topics = [pr * 100 for pr in doc_topics]
            topic_dist = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in enumerate(doc_topics)]
            print('{}: {}'.format(str(doc), topic_dist))

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