from NLP.LDA.sdg_lda import SdgLda
from NLP.LDA.ihe_lda import IheLda

from NLP.GUIDED_LDA.sdg_guided_lda import SdgGuidedLda
from NLP.GUIDED_LDA.ihe_guided_lda import IheGuidedLda

from NLP.STRING_MATCH.module_match import ModuleStringMatch
from NLP.STRING_MATCH.scopus_match import ScopusStringMatch

from NLP.LDA.predict_publication import ScopusPrediction
from NLP.VALIDATION.validate_lda import ValidateLDA

from NLP.SVM.sdg_svm_dataset import SdgSvmDataset
from NLP.SVM.sdg_svm import SdgSvm

class NLP_SECTION():
    def run_LDA_SDG(self):
        SdgLda().run()

    def run_LDA_IHE(self):
        IheLda().run()

    def run_GUIDED_LDA_SDG(self):
        SdgGuidedLda().run()

    def run_GUIDED_LDA_IHE(self):
        IheGuidedLda().run()

    def module_string_match(self):
        ModuleStringMatch().run()
    
    def scopus_string_match(self):
        ScopusStringMatch().run()

    def predictScopus(self):
        ScopusPrediction().predict()

    def validate_LDA(self):
        ValidateLDA().run()

    def create_SDG_SVM_dataset(self, modules, publications):
        SdgSvmDataset().run(modules, publications)

    def run_SVM_SDG(self):
        SdgSvm().run()