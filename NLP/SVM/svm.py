import numpy as np
import pandas as pd
import pickle

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

class Svm():
    """
        The abstract class for using the SVM linear classifier with SGD (Stochastic Gradient Descent) training.
    """

    def __init__(self):
        """
            Initializes the svm dataset, tags and sgd pipeline.
        """
        self.dataset = None # dataframe with columns {ID, Description, Tag}.
        self.tags = None # all possible tags for a document.
        self.sgd_pipeline = self.create_sgd_pipeline()

    def load_dataset(self, dataset):
        """
            Load the svm dataset with columns {ID, Description, Tag}.
        """
        print("Loading dataset...")
        self.dataset = pd.read_pickle(dataset)

    def load_tags(self, tags):
        """
            Load the possible tags for classifying a particular document.
        """
        self.tags = tags

    def create_sgd_pipeline(self):
        """
            Creates a pipeline for performing the following steps: 
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
        df = self.dataset.dropna() # remove documents from dataset which don't contain a tag.

        X = df['Description']
        y = df.iloc[:,2].astype('int') # form tag labels.

        # Partition the dataset into 70% for the training set and 30% for the test set.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Fit model with stochastic gradient descent.
        self.sgd_pipeline.fit(X_train, y_train)
        
        return X_train, X_test, y_train, y_test

    def predict(self):
        """
            Predicts tag from the preprocessed description text of the dataset.
        """
        raise NotImplementedError

    def prediction_report(self, X_test, y_test):
        """
            Prints the accuracy of the model on the test set, confusion matrix to evaluate the accuracy of classifications and builds 
            a report to demonstrate the main classification metrics.
        """
        y_pred = self.sgd_pipeline.predict(X_test)
        print('accuracy %s' % accuracy_score(y_pred, y_test))
        
        cm = confusion_matrix(y_test, y_pred)
        print(cm)

        my_tags = self.tags
        print(classification_report(y_test, y_pred, target_names=my_tags))

    def write_results(self, results_file: str):
        """
            Serializes the prediction results as a JSON file and pushes the data to MongoDB.
        """
        raise NotImplementedError

    def serialize(self, model_pkl_file: str):
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