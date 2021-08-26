import time, datetime
import json
import pymongo
import numpy as np
import pandas as pd
import ssl

from main.NLP.LDA.LDA import Lda
from main.NLP.PREPROCESSING.preprocessor import Preprocessor
from main.LOADERS.publication_loader import PublicationLoader
from main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

class IheLda(Lda):
    """
        Concrete class for mapping Scopus research publications to IHE areas of expertise using Latent Dirichlet Allocation (LDA). 
        The eta priors can be alterned to guide topic convergence given IHE-specific keywords.
    """

    def __init__(self):
        """
            Initialize state of IheLda with default preprocessor, publication data loader, scopus publications data, list of IHE-specific 
            keywords, number of IHE research expertise topics, text vectorizer and model.
        """
        self.preprocessor = Preprocessor()
        self.loader = PublicationLoader()
        self.data = None # publication dataframe with columns {DOI, Description}.
        self.keywords = None # list of IHE-specific keywords.
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 3, 1, 0.2)
        self.model = None

    def create_eta(self, priors: dict, eta_dictionary: dict) -> np.ndarray:
        """
            Sets the eta hyperparameter as a skewed prior distribution over word weights in each topic.
            IHE-specific keywords are given a greater value, aimed at guiding the topic convergence.
        """

        eta = np.full(shape=(self.num_topics, len(eta_dictionary)), fill_value=1) # topic-term matrix filled with the value 1.
        for keyword, topics in priors.items():
            keyindex = [index for index, term in eta_dictionary.items() if term == keyword]
            if len(keyindex) > 0:
                for topic in topics:
                    eta[topic, keyindex[0]] = 1e6 # increases the A-priori belief on topic keyword probability (for GuidedLDA).
                    
        # eta = np.divide(eta, eta.sum(axis=0))
        return eta

    def write_results(self, corpus, num_top_words: int, results_file: str) -> None:
        """
            Serializes the perplexity, topic-word and document-topic distributions as a JSON file and pushes the data to MongoDB.
        """
        data = {}

        # Save perplexity.
        data['Perplexity'] = self.model.log_perplexity(corpus)
        
        # Save topic-word distribution.
        data['Topic Words'] = {}
        for n in range(self.num_topics):
            data['Topic Words'][str(n + 1)] = [self.model.id2word[w]for w, p in self.model.get_topic_terms(n, topn=num_top_words)]

        # Save document-topic distribution.
        data['Document Topics'] = {}
        documents = self.data.DOI
        for d, c in zip(documents, corpus):
            doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
            data['Document Topics'][str(d)] = doc_topics

        with open(results_file, 'w') as outfile:
            json.dump(data, outfile)

        # Push data to MongoDB and serialize as JSON file.
        MongoDbPusher().ihe_prediction(data)        

    def display_topic_words(self, num_top_words: int) -> None:
        """
            Prints the topic-word distribution with num_top_words words for each IHE area of expertise.
        """
        for n in range(self.num_topics):
            print('IHE {}: {}'.format(n + 1, [self.model.id2word[w] for w, p in self.model.get_topic_terms(n, topn=num_top_words)]))

    def display_document_topics(self, corpus) -> None:
        """
            Prints the document-topic distribution for each research publication in the corpus.
        """
        documents = self.data.DOI
        count = 0
        for d, c in zip(documents, corpus):
            if count % 100 == 0:
                doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
                print('{} {}'.format(d, doc_topics))
            count += 1
    
    def run(self) -> None:
        """
            Initializes IheLda parameters, trains the model and saves the results.
        """
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        # Training parameters.
        num_publications = 30000
        
        # IHE-specific keywords.
        keywords = "main/IHE_KEYWORDS/lda_speciality_keywords.csv"

        passes = 10
        iterations = 400
        chunksize = 5000
        num_top_words = 20

        # IHE results files.
        pyldavis_html = "main/NLP/LDA/IHE_RESULTS/pyldavis.html"
        tsne_clusters_html = "main/NLP/LDA/IHE_RESULTS/tsne_clusters.html"
        model = "main/NLP/LDA/IHE_RESULTS/model.pkl"
        results = "main/NLP/LDA/IHE_RESULTS/training_results_all.json"
        
        self.load_dataset(num_publications)
        self.load_keywords(keywords)
        self.num_topics = len(pd.read_csv(keywords, nrows=0).columns.tolist())
        
        print("Training...")
        corpus = self.train(passes, iterations, chunksize)
        self.display_results(corpus, num_top_words, pyldavis_html, tsne_clusters_html)
        
        print("Saving results...")
        self.write_results(corpus, num_top_words, results)
        self.push_html_postgre("main/NLP/LDA/IHE_RESULTS/pyldavis.html", "main/NLP/LDA/IHE_RESULTS/tsne_clusters.html", "ihe")
        self.serialize(model)

        print("Done.")
