import time, datetime
import pandas as pd
import numpy as np

from NLP.SVM.svm import Svm

class SdgSvm(Svm):
    """
        Concrete class to classify SDGs for modules and publications using the Svm model.
    """

    def __init__(self):
        super().__init__()

    def write_results(self, results):
        """
            
        """
        return None

    def predict(self, X):
        """
            Predicts SDG from a list of preprocessed text.
        """
        indices = list(X.index)
        y_pred = self.sgd_pipeline.predict(X)
        for c, i in enumerate(indices):
            if c % 100 == 0:
                name = self.data.at[i, 'ID']
                prediction = y_pred[c]
                print('{}: SDG {}'.format(name, prediction))
    
    def run(self):
        """
            Trains the SVM model for clasifying SDGs using stochastic gradient descent.
        """
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        svm_dataset = "NLP/SVM/SVM_dataset.pkl"
        tags = ['SDG {}'.format(i) for i in range(1, 19)]

        # SDG results files.
        model = "NLP/SVM/SDG_RESULTS/model.pkl"
        results = "NLP/SVM/SDG_RESULTS/training_results.json"

        self.load_dataset(svm_dataset)
        self.load_tags(tags)

        print("Training...")
        X_train, X_test, y_train, y_test = self.train()

        print("Prediction report...")
        self.prediction_report(X_test, y_test)

        print("Predicting training set...")
        self.predict(X_train)

        print("Predicting test set...")
        self.predict(X_test)

        print("Saving results...")
        self.write_results(results)
        self.serialize(model)