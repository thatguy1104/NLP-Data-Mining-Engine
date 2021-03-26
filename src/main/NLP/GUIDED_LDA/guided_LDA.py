import time, datetime
import pandas as pd
import numpy as np
import pickle

from LIBRARIES.GuidedLDA import guidedlda

from sklearn.feature_extraction.text import CountVectorizer
from src.main.NLP.PREPROCESSING.preprocessor import Preprocessor
from src.main.LOADERS.loader import Loader
from src.main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

class GuidedLda():
    """
        The abstract class uses the GuidedLDA library that implements Latent Dirichlet Allocation (LDA) using collapsed Gibbs sampling.
        GuidedLDA can be guided by setting some seed words per topic, which will make the topics converge in that direction.
    """

    def __init__(self):
        """
            Initialize state of GuidedLda with abstract preprocessor, data loader, data, list of topic keywords, number of topics,
            text vectorizer and model.
        """
        self.preprocessor = Preprocessor()
        self.loader = Loader()
        self.data = None # dataframe with columns {ID, Description}.
        self.keywords = None # list of topic keywords.
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 1, 1, 1)
        self.model = None

    def write_results(self, num_top_words: int, results_file: str):
        """
            Serializes the topic-word and document-topic distributions as a JSON file and pushes the data to MongoDB.
        """
        raise NotImplementedError

    def serialize(self, model_pkl_file: str):
        """
            Serializes the GuidedLda object as a pickle file.
        """
        with open(model_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    def load_keywords(self, keywords: str):
        """
            Preprocess the list of topic keywords from the csv file path.
        """
        print("Loading keywords...")
        self.keywords = self.preprocessor.preprocess_keywords(keywords)

    def load_dataset(self, count: int):
        """
            Loads a fixed number of rows from the database as a dataframe object.
        """
        print("Loading dataset...")
        self.data = self.loader.load(count)
        print("Size before/after filtering -->",  str(count), "/", len(self.data))

    def get_vectorizer(self, min_n_gram: int, max_n_gram: int, min_df: float, max_df: float):
        """
            Returns text vectorizer with n-grams in the range [min_n_gram, max_n_gram] and the lower/upper document frequency threshold 
            for ignoring terms.
        """
        stopwords = [self.preprocessor.lemmatize(s) for s in self.preprocessor.stopwords] # lemmatize stopwords.
        return CountVectorizer(tokenizer=self.preprocessor.tokenize, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), 
                strip_accents='unicode', min_df=min_df, max_df=max_df)

    def guidedlda_model(self, iterations: int):
        """
            Returns an instance of the GuidedLDA model for the given number of topics and iterations.
        """
        return guidedlda.GuidedLDA(n_topics=self.num_topics, n_iter=iterations, random_state=42, refresh=20)

    def topic_seeds(self):
        """
            Returns the topic seeds as a dictionary with the keyword ID as keys and topic ID as values.
        """
        feature_names = self.vectorizer.get_feature_names() # list of n-grams of words.
        word2id = dict((v, i) for i, v in enumerate(feature_names)) # dictionary of word frequencies.
        seed_topics = {} # dictionary of keyword_id to topic_id.
        for topic_id, topic_keywords in enumerate(self.keywords):
            for keyword in topic_keywords:
                keyword_id = word2id.get(keyword)
                if keyword_id is not None:
                    seed_topics[keyword_id] = topic_id # one-to-one mapping from keyword_id to topic_id.
        return seed_topics

    def train(self, seed_confidence: float, iterations: int):
        """
            Trains the GuidedLDA model by calling fit_transform on the description text, creating topic seeds and fitting the model.
        """
        X = self.vectorizer.fit_transform(self.data.Description) # map description to a document-count matrix.
        seed_topics = self.topic_seeds()
        self.model = self.guidedlda_model(iterations)
        self.model.fit(X, seed_topics=seed_topics, seed_confidence=seed_confidence)

    def display_topic_words(self, num_top_words: int):
        """
            Prints the topic-word distribution with num_top_words words for each topic.
        """
        feature_names = self.vectorizer.get_feature_names()
        topic_word = self.model.topic_word_
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(feature_names)[np.argsort(topic_dist)][:-(num_top_words + 1):-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    def display_document_topics(self):
        """
            Prints the document-topic distribution for each document in the corpus.
        """
        raise NotImplementedError

    def display_results(self, num_top_words: int, pyldavis_html: str, t_sne_cluster_html: str):
        """
            Display topic-word distribution and document-topic distribution.
        """
        self.display_topic_words(num_top_words)
        self.display_document_topics()

    def run(self):
        """
            Initializes GuidedLda parameters, trains the model and saves the results.
        """
        raise NotImplementedError
