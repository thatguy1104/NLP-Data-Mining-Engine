import os
import pandas as pd
import numpy as np
import joblib

import guidedlda

from sklearn.feature_extraction.text import CountVectorizer
from preprocess import module_catalogue_tokenizer, text_lemmatizer, get_stopwords

class GuidedLDA():
    def __init__(self, data, keywords, n_iter):
        self.data = data # module-catalogue data frame with columns {ModuleID, Description}.
        self.keywords = keywords # topic keywords list.
        self.vectorizer = self.create_vectorizer(1, 4, 1, 0.4)
        self.model = self.create_model(len(keywords), n_iter, 7, 20)

    def create_vectorizer(self, min_n_gram, max_n_gram, min_df, max_df):
        stopwords = [text_lemmatizer(s) for s in get_stopwords()] # lemmatize stopwords.
        return CountVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), 
            strip_accents='unicode', min_df=min_df, max_df=max_df)

    def create_model(self, n_topics, n_iter, random_state, refresh):
        return guidedlda.GuidedLDA(n_topics=n_topics, n_iter=n_iter, random_state=random_state, refresh=refresh)

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

    def train(self, seed_confidence):
        X = self.vectorizer.fit_transform(self.data.Description) # maps description column to matrix of documents as the rows and counts as the columns.
        print("X.shape = " + str(X.shape))
        seed_topics = self.create_topic_seeds()
        self.model.fit(X, seed_topics=seed_topics, seed_confidence=seed_confidence)

    def serialize(self, filename):
        filename = filename + ".pkl"
        joblib.dump(self.model, filename)

    '''
    def display_topic_words_with_scores(self, num_top_words):
        tf_feature_names = self.vectorizer.get_feature_names()
        topic_word = self.model.topic_word_

        for i, topic_dist in enumerate(topic_word):
            result = []
            topic_dist_indices = np.argsort(topic_dist)
            print(topic_dist_indices)
            topic_words = np.array(tf_feature_names)[topic_dist_indices][:-(num_top_words + 1):-1]
            print(topic_dist)
            for j, word in enumerate(topic_words):
                word_score = str(round(topic_dist[topic_dist_indices[j]], 6))
                word_score_tuple = (word, word_score)
                result.append(str(word_score_tuple))

            print('Topic {}: {}'.format(i, ' + '.join(result)))
    '''

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
