import time, datetime
import pandas as pd
import numpy as np
import pickle

from LIBRARIES.GuidedLDA import guidedlda

from sklearn.feature_extraction.text import CountVectorizer
from NLP.PREPROCESSING.preprocessor import Preprocessor
from LOADERS.loader import Loader

class GuidedLda():
    def __init__(self):
        self.loader = Loader()
        self.preprocessor = Preprocessor()
        self.data = None # dataframe with columns {ID, Description}.
        self.keywords = None # list of topic keywords
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 1, 1, 1)
        self.model = None

    def load_keywords(self, keywords):
        print("Loading keywords...")
        self.keywords = self.preprocessor.preprocess_keywords(keywords)

    def load_dataset(self, count):
        print("Loading dataset...")
        self.data = self.loader.load(count)
        print("Size before/after filtering -->",  str(count), "/", len(self.data))

    def get_vectorizer(self, min_n_gram, max_n_gram, min_df, max_df):
        stopwords = [self.preprocessor.lemmatize(s) for s in self.preprocessor.stopwords] # lemmatize stopwords.
        return CountVectorizer(tokenizer=self.preprocessor.tokenize, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), 
                strip_accents='unicode', min_df=min_df, max_df=max_df)

    def guidedlda_model(self, iterations):
        return guidedlda.GuidedLDA(n_topics=self.num_topics, n_iter=iterations, random_state=42, refresh=20)

    def topic_seeds(self):
        feature_names = self.vectorizer.get_feature_names() # list of n-grams of words.
        word2id = dict((v, i) for i, v in enumerate(feature_names)) # dictionary of word frequencies.
        seed_topics = {} # dictionary of keyword_id to topic_id.
        for topic_id, topic_keywords in enumerate(self.keywords):
            for keyword in topic_keywords:
                keyword_id = word2id.get(keyword)
                if keyword_id is not None:
                    seed_topics.setdefault(keyword_id, []).append(topic_id) # one-to-many mapping from keyword_id to topic_id.
        return seed_topics

    def train(self, seed_confidence, iterations):
        X = self.vectorizer.fit_transform(self.data.Description) # map description to a document-count matrix.
        seed_topics = self.topic_seeds()
        self.model = self.guidedlda_model(iterations)
        self.model.fit(X, seed_topics=seed_topics, seed_confidence=seed_confidence)

    def serialize(self, model_pkl_file):
        with open(model_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    def display_topic_words(self, num_top_words):
        feature_names = self.vectorizer.get_feature_names()
        topic_word = self.model.topic_word_
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(feature_names)[np.argsort(topic_dist)][:-(num_top_words + 1):-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    def display_document_topics(self):
        doc_topic = self.model.doc_topic_
        documents = self.data.Module_ID
        for doc, doc_topics in zip(documents, doc_topic):
            doc_topics = [pr * 100 for pr in doc_topics]
            topic_dist = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in enumerate(doc_topics)]
            print('{}: {}'.format(str(doc), topic_dist))

    def display_results(self, num_top_words, pyldavis_html, t_sne_cluster_html):
        self.display_topic_words(num_top_words)
        self.display_document_topics()

    def run(self):
        raise NotImplementedError
