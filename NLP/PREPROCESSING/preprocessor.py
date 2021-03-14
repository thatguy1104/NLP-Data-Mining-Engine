import pandas as pd

from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS as gensim_stopwords
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as sklearn_stopwords

from nltk.corpus import wordnet, stopwords as nltk_stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import re
from nltk import bigrams, trigrams, pos_tag
from nltk.tokenize import word_tokenize

class Preprocessor():
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = self.get_stopwords()

    def get_stopwords(self):
        nltk_stopwords_set = set(nltk_stopwords.words('english'))
        stopwords = list(nltk_stopwords_set.union(gensim_stopwords).union(sklearn_stopwords))
        return stopwords

    def get_wordnet_pos(self, word):
        tag = pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN) # default is NOUN.

    def lemmatize(self, text):
        return self.lemmatizer.lemmatize(text, pos=self.get_wordnet_pos(text))

    def tokenize(self, text):
        text = re.sub(r'[^\w]', " ", text) # remove punctuation.
        text = re.sub(r'[\s]\d+(\.\d+)?[\s]', " ", text) # remove numbers.
        
        tokens = simple_preprocess(text, deacc=True, min_len=3, max_len=20) # lowercase and remove accents.
        tokens = [self.lemmatize(token) for token in tokens]
        return tokens

    def preprocess_keyword(self, keyword):
        return ' '.join(self.tokenize(keyword))

    def preprocess_keywords(self, keywords):
        keywords_df = pd.read_csv(keywords)
        keywords_list = []
        for column in keywords_df:
            keywords = pd.Index(keywords_df[column]).dropna()
            keywords = keywords.map(self.preprocess_keyword).drop_duplicates()
            keywords = list(keywords)
            try:
                keywords.remove('')
            except ValueError:
                pass
            keywords_list.append(keywords)
        return keywords_list