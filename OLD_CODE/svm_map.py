import pandas as pd
from NLP.SVM.svm import SVM

class Initialise_SVM_Model():
    def create(self):
        df = pd.read_pickle("NLP/SVM/SVM_dataset.pkl")
        df = df.dropna()
        svm = SVM(df)
        svm.run()