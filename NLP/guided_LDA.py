import os
import pandas as pd
import numpy as np

import guidedlda
from sklearn.feature_extraction.text import CountVectorizer
from preprocess import module_catalogue_tokenizer, get_stopwords

'''
def get_keywords(self):
    os.chdir("./MODULE_CATALOGUE/SDG_KEYWORDS")
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, self.keywords)
    df = pd.read_csv(file_path)
    df = df.dropna()

    #seed_topic_list = df.values.tolist()
    seed_topic_list = [['fruit', 'food', 'banana', 'apple'],
                        ['sport' 'football', 'basketball', 'bowling'],
                        ['ocean', 'fish']]
    for i in range(len(seed_topic_list)):
        for j in range(len(seed_topic_list[i])):
            keyword = module_catalogue_tokenizer(seed_topic_list[i][j]) # pre-process keywords
            seed_topic_list[i][j] = ''.join(keyword)
    return seed_topic_list

def data_to_dataframe(self, data):
    return pd.DataFrame(data=data,columns=["Description"])
'''

class GuidedLDA():
    '''
        data: module-catalogue DataFrame with columns {ModuleID, Description}.
        keywords: list of topic keywords.
        iterations: number of iterations to perform.
    '''
    def __init__(self, data, keywords, iterations):
        self.data = data
        self.keywords = keywords
        self.vectorizer = CountVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=get_stopwords(), ngram_range=(1,1))
        self.model = guidedlda.GuidedLDA(n_topics=len(keywords), n_iter=iterations, random_state=7, refresh=20)

    def create_topic_seeds(self):
        tf_feature_names = self.vectorizer.get_feature_names() # list of terms: words or ngrams of words.
        word2id = dict((v, i) for i, v in enumerate(tf_feature_names)) # dictionary of word frequencies.
        print(word2id)
        print()

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
        self.model.fit(X, seed_topics=seed_topics, seed_confidence=0.4)

    def display_topic_words(self, num_top_words):
        tf_feature_names = self.vectorizer.get_feature_names()
        topic_word = self.model.topic_word_
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(tf_feature_names)[np.argsort(topic_dist)][:-(num_top_words + 1):-1]
            print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    def display_document_topics(self):
        print()