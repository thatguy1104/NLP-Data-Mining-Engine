from NLP.validate import ValidateLDA
from NLP.LDA.sdg_lda import SdgLda
from NLP.GUIDED_LDA.sdg_guided_lda import SdgGuidedLda
from NLP.LDA.predict_publication import ScopusMap
from NLP.SVM.create_dataset import SVMDataset
from NLP.SVM.svm_map import Initialise_SVM_Model

class NLP_SECTION():
    def run_LDA_SDG(self):
        SdgLda().run()

    def run_GUIDED_LDA_SDG(self):
        SdgGuidedLda().run()

    def predictScopus(self):
        ScopusMap().predict()

    def validate_LDA(self):
        ValidateLDA().run()

    def create_SVM_dataset(self,):
        SVMDataset().run(True, True)

    def initialise_SVM_model(self):
        Initialise_SVM_Model().create()