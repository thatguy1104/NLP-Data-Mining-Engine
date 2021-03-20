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

    def run_LDA_SDG(self) -> None:
        """
            Runs LDA model training for Module SDG classification
        """

        SdgLda().run()

    def run_LDA_IHE(self) -> None:
        """
            Runs LDA model training for Publication IHE classification
        """

        IheLda().run()

    def run_GUIDED_LDA_SDG(self) -> None:
        """
            Runs GuidedLDA model training for Module SDG classification
        """

        SdgGuidedLda().run()

    def run_GUIDED_LDA_IHE(self) -> None:
        """
            Runs GuidedLDA model training for Publications SDG classification
        """

        IheGuidedLda().run()

    def module_string_match(self) -> None:
        """
            Perform SDG string matching (keyword occurences) for modules
        """

        ModuleStringMatch().run()
    
    def scopus_string_match(self) -> None:
        """
            Perform SDG string matching (keyword occurences) for publications
        """

        ScopusStringMatch().run()

    def predictScopus(self) -> None:
        """
            Use trained LDA model to perform SDG assignments for Scopus publications
        """

        ScopusPrediction().predict()

    def validate_LDA(self) -> None:
        """
           Validate LDA model results against string matched classification 
        """

        ValidateLDA().run()

    def create_SDG_SVM_dataset(self, modules: bool, publications: bool) -> None:
        """
            Creates the dataset needed to run SVM validation on LDA model predictions
        """
        SdgSvmDataset().run(modules, publications)

    def run_SVM_SDG(self) -> None:
        """
            Runs SVM model training for Modules & Publications SDG classification
        """
        SdgSvm().run()


