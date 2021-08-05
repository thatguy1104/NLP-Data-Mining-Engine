import time, datetime
import pandas as pd
import numpy as np
import json

from main.NLP.SVM.svm import Svm
from main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from main.NLP.PREPROCESSING.preprocessor import Preprocessor

class SdgSvm(Svm):
    """
        Concrete class to classify SDGs for modules and publications using the Svm model.
    """

    def __init__(self):
        super().__init__()

    def write_results(self, X_test, y_test, results_file: str) -> None:
        """
            Serializes the prediction results as a JSON file and pushes the data to MongoDB.
        """
        X_description = self.dataset['Description'] # includes modules and publications that may contain a None tag.
        X_id = self.dataset['ID']

        accuracy, cm, classification_metrics = self.prediction_report(X_test, y_test)

        data = {}

        # Save prediction report metrics.
        data['Accuracy'] = accuracy
        data['Confusion Matrix'] = cm.tolist()
        data['Classification Report'] = classification_metrics

        # Save probability predictions for modules and publications.
        data['Module'] = {}
        data['Publication'] = {}

        is_module = lambda x_id : len(x_id) == 8 # matches Module_ID for UCL modules.
    
        y_pred = self.sgd_pipeline.predict_proba(X_description)
        for i, probabilities in enumerate(y_pred):
            x_id = X_id[i]
            if is_module(x_id):
                # x_id is a Module_ID
                data['Module'][x_id] = probabilities.tolist()
            else:
                # x_id is a DOI
                data['Publication'][x_id] = probabilities.tolist()
        
        # Push data to MongoDB and serialize as JSON file.
        MongoDbPusher().svm_sdg_predictions(data)
        with open(results_file, 'w') as outfile:
            json.dump(data, outfile)

    def print_predictions(self) -> None:
        """
            Predicts SDG for each document description in the dataset, including those in the training set, test set
            and those not in either (because the SDG tag is None).
        """
        X_description = self.dataset['Description'] # includes modules and publications that may contain a None tag.
        X_id = self.dataset['ID']

        y_pred = self.sgd_pipeline.predict_proba(X_description)
        for i in range(len(y_pred)):
            if i % 100 == 0:
                print('{}: SDG probabilities = {}'.format(X_id[i], y_pred[i]))

    def print_prediction_report(self, X_test, y_test) -> None:
        '''
            Builds a full prediction report including the accuracy, confusion matrix and other classification 
            metrics, printing these results to the terminal.
        '''
        accuracy, cm, classification_metrics = self.prediction_report(X_test, y_test)
        print('accuracy %s' % accuracy)
        print(cm)
        print(classification_metrics)

    def print_text_prediction(self, text) -> None:
        """
            Predicts probabilities of SDGs given any random text input.
        """
        text = Preprocessor().preprocess(text)
        y_pred = self.sgd_pipeline.predict_proba([text])
        for i in range(len(y_pred)):
            print('SDG probabilities = {}'.format(y_pred[i]))
            print('SDG = {}'.format(np.argmax(y_pred) + 1))

    def run(self) -> None:
        """
            Trains the SVM model for clasifying SDGs using stochastic gradient descent.
        """
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        svm_dataset = "main/NLP/SVM/dataset.csv"
        tags = ['SDG {}'.format(i) for i in range(1, 19)] # SDG tags.

        # SDG results files.
        model = "main/NLP/SVM/SDG_RESULTS/model.pkl"
        results = "main/NLP/SVM/SDG_RESULTS/training_results.json"

        self.load_dataset(svm_dataset)
        self.load_tags(tags)

        print("Training...")
        X_train, X_test, y_train, y_test = self.train()

        print("Prediction report...")
        self.print_prediction_report(X_test, y_test)

        print("Predicting dataset")
        self.print_predictions()

        print("Saving results...")
        self.write_results(X_test, y_test, results)
        self.serialize(model)
