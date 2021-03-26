import time, datetime
import json
import numpy as np
import pymongo
import ssl

from src.main.NLP.GUIDED_LDA.guided_LDA import GuidedLda
from src.main.NLP.PREPROCESSING.module_preprocessor import ModuleCataloguePreprocessor
from src.main.LOADERS.module_loader import ModuleLoader
from src.main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

class SdgGuidedLda(GuidedLda):
    """
        Concrete class for mapping UCL modules to UN SDGs (United Nations Sustainable Development Goals) using GuidedLDA with collapsed Gibbs sampling.
        GuidedLDA can be guided by setting some seed words per topic, which will make the topics converge in that direction.
    """

    def __init__(self):
        """
            Initialize state of SdgGuidedLda with module-catalogue preprocessor, module data loader, module data, list of SDG-specific keywords, 
            number of SDGs, text vectorizer and model.
        """
        self.preprocessor = ModuleCataloguePreprocessor()
        self.loader = ModuleLoader()
        self.data = None # module-catalogue dataframe with columns {ModuleID, Description}.
        self.keywords = None # list of SDG-specific keywords.
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
        documents = self.data.Module_ID
        for doc, doc_topics in zip(documents, doc_topic):
            doc_topics = [pr * 100 for pr in doc_topics]
            topic_dist = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in enumerate(doc_topics)]
            data['Document Topics'][str(doc)] = topic_dist

        # Push data to MongoDB and serialize as JSON file.
        MongoDbPusher().module_prediction(data)
        with open(results_file, 'w') as outfile:
            json.dump(data, outfile)

    def display_document_topics(self):
        """
            Prints the document-topic distribution for each module in the corpus.
        """
        doc_topic = self.model.doc_topic_
        documents = self.data.Module_ID
        for doc, doc_topics in zip(documents, doc_topic):
            doc_topics = [pr * 100 for pr in doc_topics]
            topic_dist = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in enumerate(doc_topics)]
            print('{}: {}'.format(str(doc), topic_dist))

    def run(self):
        """
            Initializes SdgGuidedLda parameters, trains the model and saves the results.
        """
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        # Training parameters.
        num_modules = "MAX"
        # SDG-specific keywords.
        keywords = "src/main/SDG_KEYWORDS/SDG_Keywords.csv"
        iterations = 400
        seed_confidence = 1.0
        num_top_words = 20

        # SDG results files.
        pyldavis_html = "src/main/NLP/GUIDED_LDA/SDG_RESULTS/pyldavis.html"
        tsne_clusters_html = "src/main/NLP/GUIDED_LDA/SDG_RESULTS/tsne_clusters.html"
        model = "src/main/NLP/GUIDED_LDA/SDG_RESULTS/model.pkl"
        results = "src/main/NLP/GUIDED_LDA/SDG_RESULTS/training_results.json"
        
        self.load_dataset(num_modules)
        self.load_keywords(keywords)
        self.num_topics = len(self.keywords)

        print("Training...")
        self.train(seed_confidence, iterations)
        self.display_results(num_top_words, pyldavis_html, tsne_clusters_html)

        print("Saving results...")
        self.write_results(num_top_words, results) # record current results.
        self.serialize(model)

        print("Done.")
