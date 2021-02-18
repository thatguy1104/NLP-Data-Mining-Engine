import os
import pandas as pd
import numpy as np
import joblib

import guidedlda
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from preprocess import module_catalogue_tokenizer, get_stopwords

class GuidedLDA():
    def __init__(self, data, keywords, iterations):
        self.data = data # module-catalogue DataFrame with columns {ModuleID, Description}.
        self.keywords = keywords # list of topic keywords.
        self.vectorizer = CountVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=get_stopwords(), ngram_range=(1,4))
        #self.vectorizer = TfidfVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=get_stopwords(), ngram_range=(1,4))
        self.model = guidedlda.GuidedLDA(n_topics=len(keywords), n_iter=iterations, random_state=5, refresh=20)

    def create_topic_seeds(self):
        tf_feature_names = self.vectorizer.get_feature_names() # list of terms: words or ngrams of words.
        word2id = dict((v, i) for i, v in enumerate(tf_feature_names)) # dictionary of word frequencies.
        seed_topics = {} # dictionary: word_id to topic_id.
        for t_id, st in enumerate(self.keywords):
            for word in st:
                id = word2id.get(word)
                if id is not None:
                    seed_topics[id] = t_id
        return seed_topics

    def train(self):
        X = self.vectorizer.fit_transform(self.data.Description) # maps description column to matrix of documents as the rows and counts as the columns.
        print(X.shape)
        seed_topics = self.create_topic_seeds()
        self.model.fit(X, seed_topics=seed_topics, seed_confidence=1)

    def serialize(self, filename):
        filename = filename + ".pkl"
        joblib.dump(self.model, filename)

    def display_topic_words(self, num_top_words):
        tf_feature_names = self.vectorizer.get_feature_names()
        topic_word = self.model.topic_word_
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(tf_feature_names)[np.argsort(topic_dist)][:-(num_top_words + 1):-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    def display_document_topics(self):
        tf_feature_names = self.vectorizer.get_feature_names()
        doc_topic = self.model.doc_topic_
        n_topics = self.model.n_topics
        columns = ['topic {}'.format(i) for i in range(n_topics)] # column labels for all topics.
        df = pd.DataFrame(doc_topic, columns = columns) # document-topics dataframe.
        print(df.round(2).head(10))

    def display_document_topic_words(self, num_top_words):
        print('-----------------------------------------------------')
        self.display_topic_words(num_top_words)
        print('-----------------------------------------------------')
        self.display_document_topics()
        print('-----------------------------------------------------')
