import time, datetime
import pandas as pd

from NLP.SVM.svm import Svm

class SdgSvm(Svm):
    def __init__(self):
        super().__init__()

    def run(self):
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        svm_dataset = "NLP/SVM/SVM_dataset.pkl"
        tags = ['SDG {}'.format(i) for i in range(1, 19)]

        model = "NLP/SVM/SDG_RESULTS/model.pkl"
        results = "NLP/SVM/SDG_RESULTS/training_results.json"

        self.load_dataset(svm_dataset)
        self.load_tags(tags)

        print("Training...")
        X_test, y_test = self.train()
        self.prediction_report(X_test, y_test)

        print("Saving results...")
        #self.write_results(corpus, num_top_words, results) # record current results.
        self.serialize(model)