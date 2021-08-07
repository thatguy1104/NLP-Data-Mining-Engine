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
    """
        Default class for preprocessing natural language text. 
    """

    def __init__(self):
        """
            Initialize lemmatizer and stopwords.
        """
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = self.get_stopwords()

    def get_stopwords(self) -> list:
        """
            Returns the union of NLTK and Gensim stopwords sets.
        """
        nltk_stopwords_set = set(nltk_stopwords.words('english'))
        stopwords = list(nltk_stopwords_set.union(gensim_stopwords).union(sklearn_stopwords))
        return stopwords

    def get_wordnet_pos(self, word: str):
        """
            Maps treebank tags to wordnet part of speech names.
        """
        tag = pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN) # default is NOUN.

    def lemmatize(self, text: str) -> str:
        return self.lemmatizer.lemmatize(text, pos=self.get_wordnet_pos(text))

    def tokenize(self, text: str) -> list:
        """
            Normalize text, convert to list of lowercase tokens and lemmatize tokens.
        """
        text = re.sub(r'[^\w]', " ", text) # remove punctuation.
        text = re.sub(r'[\s]\d+(\.\d+)?[\s]', " ", text) # remove numerical values.
        
        tokens = simple_preprocess(text, deacc=True, min_len=3, max_len=20) # lowercase and remove accents.
        tokens = [self.lemmatize(token) for token in tokens]
        return tokens

    def tokenize_not_lemmatize(self, text: str) -> list:
        """
            Normalize text, convert to list of lowercase tokens and lemmatize tokens.
        """
        text = re.sub(r'[^\w]', " ", text)  # remove punctuation.
        text = re.sub(r'[\s]\d+(\.\d+)?[\s]', " ", text) # remove numerical values.
        # tokens = simple_preprocess(text, deacc=True, min_len=3, max_len=20)  # lowercase and remove accents.
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        return text

    def preprocess(self, text: str) -> str:
        """
            Helper function for preprocessing text by tokenizing and removing stopwords.
        """
        tokens = self.tokenize(text)
        tokens = [token for token in tokens if token not in self.stopwords]
        return " ".join(tokens)

    def preprocess_keyword(self, keyword: str) -> str:
        return ' '.join(self.tokenize(keyword))

    def preprocess_keywords(self, keywords: str) -> list:
        """
            Preprocess keywords by reading csv file, tokenizing and removing duplicates. Returns a list of topic keywords.
        """
        keywords_df = pd.read_csv(keywords)
        keywords_list = []
        for column in keywords_df:
            keywords = pd.Index(keywords_df[column]).dropna()
            keywords = keywords.map(self.preprocess_keyword).drop_duplicates() # remove duplicate keywords.
            keywords = list(keywords)
            try:
                keywords.remove('')
            except ValueError:
                pass
            keywords_list.append(keywords)
        return keywords_list
