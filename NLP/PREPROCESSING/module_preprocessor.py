import pandas as pd

from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import re

from NLP.PREPROCESSING.preprocessor import Preprocessor

class ModuleCataloguePreprocessor(Preprocessor):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = self.get_stopwords()

    def get_stopwords(self):
        english_stopwords = set(super().get_stopwords())
        module_catalogue_stopwords = self.module_catalogue_stopwords()
        return list(english_stopwords.union(module_catalogue_stopwords))

    def module_catalogue_stopwords(self):
        df = pd.read_csv("MODULE_CATALOGUE/module_catalogue_stopwords.csv", index_col=False)['Stopwords']
        preprocessed_stopwords = [self.lemmatize(stopword) for stopword in list(df)] 
        return set(preprocessed_stopwords)

    def tokenize(self, text):
        text = re.sub(r'[A-Z]{4}\d{4}', " ", text) # remove UCL module codes.
        text = re.sub(r'[/]', " ", text) # separate forward slashes
        text = re.sub(r'[\s]\d+(\.\d+)?[\s]', " ", text) # remove numbers.
        text = re.sub(r'[^\w]', " ", text) # remove punctuation.

        tokens = simple_preprocess(text, deacc=True, min_len=3, max_len=20) # lowercase and remove accents.
        tokens = [self.lemmatize(token) for token in tokens]
        return tokens