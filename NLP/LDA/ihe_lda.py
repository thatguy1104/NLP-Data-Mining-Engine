import time, datetime
import json
import pymongo
import numpy as np
import ssl

from NLP.LDA.LDA import Lda
from NLP.PREPROCESSING.preprocessor import Preprocessor
from LOADERS.publication_loader import PublicationLoader
from MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

class IheLda(Lda):
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.loader = PublicationLoader()
        self.mongodb_pusher = MongoDbPusher()
        self.data = None # publication dataframe with columns {DOI, Description}.
        self.keywords = None # list of IHE-specific keywords.
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 3, 1, 0.2)
        self.model = None

    def create_eta(self, priors, eta_dictionary):
        # (n_topics, n_terms) matrix filled with 1s.
        eta = np.full(shape=(self.num_topics, len(eta_dictionary)), fill_value=1)
        for keyword, topics in priors.items():
            keyindex = [index for index, term in eta_dictionary.items() if term == keyword]
            if len(keyindex) > 0:
                for topic in topics:
                    eta[topic, keyindex[0]] = 1e6
                    
        # eta = np.divide(eta, eta.sum(axis=0))
        return eta

    def write_results(self, corpus, num_top_words, results_file):
        data = {}
        data['Perplexity'] = self.model.log_perplexity(corpus)

        data['Topic Words'] = {}
        for n in range(self.num_topics):
            data['Topic Words'][str(n + 1)] = [self.model.id2word[w]for w, p in self.model.get_topic_terms(n, topn=num_top_words)]

        data['Document Topics'] = {}
        documents = self.data.DOI
        for d, c in zip(documents, corpus):
            doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
            data['Document Topics'][str(d)] = doc_topics

        self.mongodb_pusher.ihe_prediction(data) # push to mongo.
        with open(results_file, 'w') as outfile:
            json.dump(data, outfile)

    def display_topic_words(self, num_top_words):
        for n in range(self.num_topics):
            print('IHE {}: {}'.format(n + 1, [self.model.id2word[w] for w, p in self.model.get_topic_terms(n, topn=num_top_words)]))

    def display_document_topics(self, corpus):
        documents = self.data.DOI
        count = 0
        for d, c in zip(documents, corpus):
            if count % 100 == 0:
                doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
                print('{} {}'.format(d, doc_topics))
            count += 1
    
    def run(self):
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        num_publications = "MAX"
        keywords = "IHE_KEYWORDS/ihe_keywords.csv"
        passes = 10
        iterations = 400
        chunksize = 30000
        num_top_words = 20

        pyldavis_html = "NLP/LDA/IHE_RESULTS/pyldavis.html"
        tsne_clusters_html = "NLP/LDA/IHE_RESULTS/tsne_clusters.html"
        model = "NLP/LDA/IHE_RESULTS/model.pkl"
        results = "NLP/LDA/IHE_RESULTS/training_results.json"

        self.load_dataset(num_publications)
        self.load_keywords(keywords)
        self.num_topics = len(self.keywords)
        
        print("Training...")
        corpus = self.train(passes, iterations, chunksize)
        self.display_results(corpus, num_top_words, pyldavis_html, tsne_clusters_html)

        print("Saving results...")
        self.write_results(corpus, num_top_words, results) # record current results.
        self.serialize(model)