import gensim
import numpy as np
import pandas as pd
import nltk

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from preprocess import module_catalogue_tokenizer, text_lemmatizer, get_stopwords

class SVM():
    def __init__(self, data):
        self.data = data # dataframe with columns {ModuleID, Description, SDG}.
        self.tags = ['SDG {}'.format(i) for i in range(1, 19)]
        self.sgd = self.create_sgd()

    def tokenizer(self, text):
        return " ".join(module_catalogue_tokenizer(text))

    def create_sgd(self):
        sgd = Pipeline([('vect', CountVectorizer()), 
                        ('tfidf', TfidfTransformer()), 
                        ('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, random_state=42, max_iter=100, tol=None))])
        return sgd

    def train(self):
        X = self.data['Description'].apply(self.tokenizer) # preprocess module descriptions.
        y = self.data['SDG'].astype('int') # SDG labels.

        # Partition dataset into 70% train and 30% test.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Fit model.
        self.sgd.fit(X_train, y_train)
        return X_test, y_test

    def predict(self, X_test, y_test):
        y_pred = self.sgd.predict(X_test)
        my_tags = self.tags

        print('accuracy %s' % accuracy_score(y_pred, y_test))
        print(classification_report(y_test, y_pred, target_names=my_tags))

    def run(self):
        X_test, y_test = self.train()
        print()
        self.predict(X_test, y_test)

df = pd.read_pickle("NLP/ModelResults/SVM_dataset.pkl")
df = df.dropna()

svm = SVM(df)
svm.run()