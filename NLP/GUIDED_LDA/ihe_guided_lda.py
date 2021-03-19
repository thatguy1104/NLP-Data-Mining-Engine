import time, datetime
import json
import numpy as np
import pymongo
import ssl

from LIBRARIES.GuidedLDA import guidedlda

from NLP.GUIDED_LDA.guided_LDA import GuidedLda
from NLP.PREPROCESSING.preprocessor import Preprocessor
from LOADERS.publication_loader import PublicationLoader
from MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

class IheGuidedLda(GuidedLda):
    """
        Concrete class for mapping Scopus research publications to IHE areas of expertise using GuidedLDA with collapsed Gibbs sampling.
        GuidedLDA can be guided by setting some seed words per topic, which will make the topics converge in that direction.
    """

    def __init__(self):
        """
            Initialize state of IheGuidedLda with default preprocessor, publication data loader, scopus publications data, list of IHE-specific 
            keywords, number of IHE research expertise topics, text vectorizer and model.
        """
        self.preprocessor = Preprocessor()
        self.loader = PublicationLoader()
        self.data = None # publication dataframe with columns {DOI, Description}.
        self.keywords = None # list of IHE-specific keywords.
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 4, 1, 0.4)
        self.model = None

    def write_results(self, num_top_words: int, results_file: str):
        """
            Serializes the log-likelihood, topic-word and document-topic distributions as a JSON file and pushes the data to MongoDB.
        """
        feature_names = self.vectorizer.get_feature_names()
        data = {}

        # Save log-likelihood.
        data['Log Likelihood'] = self.model.loglikelihood()

        # Save topic-word distribution.
        data['Topic Words'] = {}
        topic_word = self.model.topic_word_
        for n, topic_dist in enumerate(topic_dist):
            topic_words = np.array(feature_names)[np.argsort(topic_dist)][:-(num_top_words + 1):-1]
            data['Topic Words'][str(n + 1)] = topic_words

        # Save document-topic distribution.
        data['Document Topics'] = {}
        doc_topic = self.model.doc_topic_
        documents = self.data.DOI
        for doc, doc_topics in zip(documents, doc_topic):
            doc_topics = [pr * 100 for pr in doc_topics]
            topic_dist = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in enumerate(doc_topics)]
            data['Document Topics'][str(doc)] = topic_dist

        # Push data to MongoDB and serialize as JSON file.
        MongoDbPusher().ihe_prediction(data)
        with open(results_file, 'w') as outfile:
            json.dump(data, outfile)

    def display_document_topics(self):
        """
            Prints the document-topic distribution for each research publication in the corpus.
        """
        doc_topic = self.model.doc_topic_
        documents = self.data.DOI
        for doc, doc_topics in zip(documents, doc_topic):
            doc_topics = [pr * 100 for pr in doc_topics]
            topic_dist = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in enumerate(doc_topics)]
            print('{}: {}'.format(str(doc), topic_dist))

    def run(self):
        """
            Initializes IheGuidedLda parameters, trains the model and saves the results.
        """
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        # Training parameters.
        num_publications = "MAX"
        keywords = "IHE_KEYWORDS/ihe_keywords.csv" # IHE-specific keywords.
        iterations = 400
        seed_confidence = 1.0
        num_top_words = 20

        # IHE results files.
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
        self.write_results(num_top_words, results)
        self.serialize(model)

        print("Done.")