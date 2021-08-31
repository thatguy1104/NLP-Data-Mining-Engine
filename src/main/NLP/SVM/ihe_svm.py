import time, sys
import datetime
import pandas as pd
import numpy as np
import json

from main.NLP.SVM.svm import Svm
from main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher
from main.NLP.PREPROCESSING.preprocessor import Preprocessor
from main.LOADERS.publication_loader import PublicationLoader

class IheSvm(Svm):
    """
        Concrete class to classify SDGs for modules and publications using the Svm model.
    """

    def __init__(self):
        super().__init__()
    
    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def write_results(self, X_test, y_test, results_file: str) -> None:
        """
            Serializes the prediction results as a JSON file and pushes the data to MongoDB.
        """
        X_description = self.dataset['Description']  # includes modules and publications that may contain a None tag.
        X_id = self.dataset['ID']

        accuracy, cm, classification_metrics = self.prediction_report(X_test, y_test)
        data = {}

        # Save prediction report metrics.
        data['Accuracy'] = accuracy
        data['Confusion Matrix'] = cm.tolist()
        data['Classification Report'] = classification_metrics

        # Save probability predictions for modules and publications.
        data['Publication'] = {}

        # matches Module_ID for UCL modules.
        def is_module(x_id): return len(x_id) == 8

        y_pred = self.sgd_pipeline.predict_proba(X_description)
        for i, probabilities in enumerate(y_pred):
            x_id = X_id[i]
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
        X_description = self.dataset['Description']  # includes modules and publications that may contain a None tag.
        X_id = self.dataset['ID']

        y_pred = self.sgd_pipeline.predict_proba(X_description)
        for i in range(len(y_pred)):
            if i % 100 == 0:
                print('{}: IHE probabilities = {}'.format(X_id[i], y_pred[i]))

    def print_prediction_report(self, X_test, y_test) -> None:
        '''
            Builds a full prediction report including the accuracy, confusion matrix and other classification 
            metrics, printing these results to the terminal.
        '''
        accuracy, cm, classification_metrics = self.prediction_report(X_test, y_test)
        print('accuracy %s' % accuracy)
        print(cm)
        print(classification_metrics)

    def print_text_prediction(self, text: str) -> None:
        """
            Predicts probabilities of SDGs given any random text input.
        """
        text = Preprocessor().preprocess(text)
        y_pred = self.sgd_pipeline.predict_proba([text])
        for i in range(len(y_pred)):
            print('IHE probabilities = {}'.format(y_pred[i]))
            print('IHE = {}'.format(np.argmax(y_pred) + 1))

    def make_text_predictions(self) -> None:
        """
            Predicts probabilities of IHEs for unseen publications
        """
        publication_loader = PublicationLoader()
        preprocessor = Preprocessor()

        with open("main/NLP/SVM/IHE_RESULTS/training_results.json") as f:
            existing_classifications = json.load(f)["Publication"]

        df_publications = publication_loader.load("MAX")
        difference = pd.DataFrame(columns=df_publications.columns)

        dois = list(self.dataset['ID'])
        l = len(df_publications)
        for i in range(l):
            self.__progress(i, l, "(SVM) Classifying unseen publications")
            all_doi = list(df_publications['DOI'][0])[i]
            
            if all_doi not in dois:            
                row = df_publications.loc[df_publications["DOI"] == all_doi]
                title = row['Title'][0]
                description = list(df_publications['Description'][0])[i]
                
                data = [all_doi, title, description]
                row_elem = pd.DataFrame([data], columns=df_publications.columns)
                difference = difference.append(row_elem, ignore_index=True)

        difference = difference.reset_index()

        for index, row in difference.iterrows():
            title = row['Title']
            description = row['Description']
            text = preprocessor.preprocess(description)
            y_pred = self.sgd_pipeline.predict_proba([text])[0]
            existing_classifications[row['DOI']] = y_pred.tolist()
        
        with open("main/NLP/SVM/IHE_RESULTS/training_results.json", "w") as f:
            json.dump(existing_classifications, f)

    def run(self) -> None:
        """
            Trains the SVM model for clasifying SDGs using stochastic gradient descent.
        """
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        svm_dataset = "main/NLP/SVM/SVM_dataset_ihe.csv"
        
        tags = ['IHE {}'.format(i) for i in range(1, 21)]  # IHE tags.

        # SDG results files.
        model = "main/NLP/SVM/IHE_RESULTS/model.pkl"
        results = "main/NLP/SVM/IHE_RESULTS/training_results.json"

        self.load_dataset(svm_dataset)
        self.load_tags(tags)
        print("Loaded dataset: size =", len(self.dataset))

        print("Training...")
        X_train, X_test, y_train, y_test = self.train()

        print("Prediction report...")
        self.print_prediction_report(X_test, y_test)

        print("Predicting dataset")
        self.print_predictions()

        print("Saving results...")
        self.write_results(X_test, y_test, results)
        self.serialize(model)

        print("Classifying the rest of publications")
        self.make_text_predictions()

        print("Done.")
