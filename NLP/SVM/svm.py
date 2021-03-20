import numpy as np
import pandas as pd
import pickle

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

from NLP.PREPROCESSING.preprocessor import Preprocessor

class Svm():
    """
        The abstract class for using the SVM linear classifier with SGD (Stochastic Gradient Descent) training.
    """

    def __init__(self):
        """
            Initializes the preprocessor, svm dataset, tags and sgd pipeline.
        """
        self.preprocessor = Preprocessor()
        self.data = None # dataframe with columns {ID, Description, Tag}.
        self.tags = None # all possible tags for a document.
        self.sgd_pipeline = self.create_sgd_pipeline()

    def load_dataset(self, dataset):
        """
            Loads the svm dataset with columns {ID, Description, Tag}.
        """
        df = pd.read_pickle(dataset)
        df = df.dropna()
        self.data = df

    def load_tags(self, tags):
        """
            Loads the possible tags for classifying a particular document.
        """
        self.tags = tags

    def tokenizer(self, text):
        """
            Helper function for tokenizing text.
        """
        return " ".join(self.preprocessor.tokenize(text))

    def create_sgd_pipeline(self):
        """
            Creates the pipeline for performing the following steps: 
                - vectorizing text for a document.
                - transforming counts to a TF-IDF representation.
                - SGD classifier for fitting a linear model with stochastic gradient descent.
        """
        sgd_pipeline = Pipeline([('vect', CountVectorizer()), 
                            ('tfidf', TfidfTransformer()), 
                            ('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, random_state=42, max_iter=100, tol=None))])
        return sgd_pipeline

    def train(self):
        """
            Trains the SVM model using stochastic gradient descent.
        """
        X = self.data['Description'].apply(self.tokenizer) # preprocess description.
        y = self.data.iloc[:,0].astype('int') # form tag labels.

        # Partition the dataset into 70% training set and 30% test set.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Fit model with stochastic gradient descent.
        self.sgd.fit(X_train, y_train)

        return X_train, X_test, y_train, y_test

    def predict(self, X):
        """
            Predicts tag from a list of preprocessed text.
        """
        raise NotImplementedError

    def prediction_report(self, X_test, y_test):
        """
            Prints the accuracy of the model on the test set, confusion matrix to evaluate the accuracy of classifications and builds 
            a report to demonstrate the main classification metrics.
        """
        y_pred = self.sgd.predict(X_test)
        print('accuracy %s' % accuracy_score(y_pred, y_test))
        
        cm = confusion_matrix(y_test, y_pred)
        print(cm)

        my_tags = self.tags
        print(classification_report(y_test, y_pred, target_names=my_tags))

    def write_results(self, corpus, num_top_words, results_file):
        """
            Serializes the prediction results as a JSON file and pushes the data to MongoDB.
        """
        raise NotImplementedError

    def serialize(self, model_pkl_file):
        """
            Serializes the Svm model as a pickle file.
        """
        with open(model_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    def run(self):
        """
            Initializes Svm parameters, trains the model and saves the results.
        """
        raise NotImplementedError