from NLP.validate import ValidateLDA
from NLP.LDA.LDA_map import Initialise_LDA_Model
from NLP.LDA.predict_publication import ScopusMap


class NLP_SECTION():

    def merge_SDG_keywords(self):
        pass

    def initialise_LDA_model(self):
        Initialise_LDA_Model().create()

    def predictScopus(self):
        ScopusMap().predict()

    def validate(self):
        ValidateLDA().run()
