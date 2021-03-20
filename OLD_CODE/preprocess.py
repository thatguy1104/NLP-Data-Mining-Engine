import os
import pandas as pd

from gensim.parsing.preprocessing import STOPWORDS as gensim_stopwords
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as sklearn_stopwords

from nltk.corpus import wordnet, stopwords as nltk_stopwords
from nltk import bigrams, trigrams, pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import re 

def get_stopwords():
    nltk_stopwords_set = set(nltk_stopwords.words('english'))
    module_catalogue_stopwords = preprocess_module_catalogue_stopwords()
    stopwords = list(nltk_stopwords_set.union(gensim_stopwords).union(sklearn_stopwords).union(module_catalogue_stopwords))
    return stopwords

def preprocess_module_catalogue_stopwords():
    df = pd.read_csv("MODULE_CATALOGUE/module_catalogue_stopwords.csv", index_col=False)['Stopwords']
    preprocessed_stopwords = [text_lemmatizer(w) for w in list(df)] 
    return set(preprocessed_stopwords)

def get_wordnet_pos(word):
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN) # default is NOUN.

def text_lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    text = lemmatizer.lemmatize(text, pos=get_wordnet_pos(text))
    return text

def module_catalogue_tokenizer(text):
    # Normalization
    text = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text) # replace UCL module codes.
    text = re.sub(r'[/]', " ", text) # separate forward slashes
    text = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', text) # replace numbers.
    text = re.sub(r'[^\w]', " ", text) # remove punctuation.
    
    # Tokenization
    text = text.lower()
    tokens = [word for word in word_tokenize(text)]
    tokens = [word for word in tokens if len(word) > 2]
    tokens = [text_lemmatizer(t) for t in tokens]

    return tokens

def preprocess_keyword(keyword):
    return ' '.join(module_catalogue_tokenizer(keyword))

def preprocess_keywords(file_name):
    df = pd.read_csv(file_name)

    # convert keywords dataframe to list of keywords.
    keywords_list = []
    for column in df:
        keywords = pd.Index(df[column]).dropna()
        keywords = keywords.map(preprocess_keyword).drop_duplicates()
        keywords = list(keywords)
        try:
            keywords.remove('')
        except ValueError:
            pass
        keywords_list.append(keywords)
    return keywords_list

def print_keywords():
    for keywords in preprocess_keywords("MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv"):
        print(keywords)
        print()
