from NLP.VALIDATION.validate_lda import ValidateLDA
from NLP.LDA.sdg_lda import SdgLda
# from NLP.GUIDED_LDA.sdg_guided_lda import SdgGuidedLda
from NLP.LDA.predict_publication import ScopusPrediction
from NLP.SVM.create_dataset import SVMDataset
from NLP.SVM.sdg_svm import SdgSvm
from NLP.STRING_MATCH.module_match import ModuleStringMatch
from NLP.STRING_MATCH.scopus_match import ScopusStringMatch

class NLP_SECTION():
    def run_LDA_SDG(self):
        SdgLda().run()

    def run_GUIDED_LDA_SDG(self):
        # SdgGuidedLda().run()
        pass

    def module_string_match(self):
        ModuleStringMatch().run()
    
    def scopus_string_match(self):
        ScopusStringMatch().run()

    def predictScopus(self):
        ScopusPrediction().predict()

    def validate_LDA(self):
        ValidateLDA().run()

    def create_SVM_dataset(self,):
        SVMDataset().run(True, True)

    def run_SVM_SDG(self):
        SdgSvm().run()
