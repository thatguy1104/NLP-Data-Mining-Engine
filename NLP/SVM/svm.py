import numpy as np
import pandas as pd
import pickle

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

from NLP.PREPROCESSING.preprocessor import Preprocessor

class Svm():
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.data = None # dataframe with columns {ID, Description, Tag}.
        self.tags = None # all possible tags for a document.        
        self.sgd = self.create_sgd()

    def load_dataset(self, dataset):
        df = pd.read_pickle(dataset)
        df = df.dropna()
        self.data = df

    def load_tags(self, tags):
        self.tags = tags

    def sgd_tokenizer(self, text):
        return " ".join(self.preprocessor.tokenize(text))

    def create_sgd(self):
        sgd = Pipeline([('vect', CountVectorizer()), 
                        ('tfidf', TfidfTransformer()), 
                        ('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, random_state=42, max_iter=100, tol=None))])
        return sgd

    def train(self):
        X = self.data['Description'].apply(self.sgd_tokenizer) # preprocess description.
        y = self.data.iloc[:,0].astype('int') # tag labels.

        # Partition dataset into 70% training set and 30% test set.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Fit model.
        self.sgd.fit(X_train, y_train)
        return X_test, y_test

    def prediction_report(self, X_test, y_test):
        y_pred = self.sgd.predict(X_test)
        my_tags = self.tags

        print('accuracy %s' % accuracy_score(y_pred, y_test))
        print(classification_report(y_test, y_pred, target_names=my_tags))

    def push_to_mongo(self, data):
        raise NotImplementedError

    def write_results(self, corpus, num_top_words, results_file):
        raise NotImplementedError

    def serialize(self, model_pkl_file):
        with open(model_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    def run(self):
        raise NotImplementedError