
import os
import pandas as pd

from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS as gensim_stopwords

from nltk import bigrams, trigrams, pos_tag
from nltk.corpus import wordnet, stopwords as nltk_stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import re 

'''
Union of the stopwords from the gensim and nltk preprocessing packages.
'''
def get_stopwords():
    nltk_stopwords_set = set(nltk_stopwords.words('english'))
    return gensim_stopwords.union(nltk_stopwords_set)

'''
Maps treebank tags to wordnet tags of the form: NN, JJ, VB, RB.
'''
def get_wordnet_pos(treebank_word):
    if treebank_word.startswith('J'):
        return wordnet.ADJ
    elif treebank_word.startswith('V'):
        return wordnet.VERB
    elif treebank_word.startswith('N'):
        return wordnet.NOUN
    elif treebank_word.startswith('R'):
        return wordnet.ADV
    return None

def lemmatize_stem(tokens):
    result = []
    stemmer = SnowballStemmer('english')
    lemmatizer = WordNetLemmatizer()
    tagged = pos_tag(tokens) # part of speech tagger
    for word, tag in tagged:
        wordnet_tag = get_wordnet_pos(tag)
        if wordnet_tag is None:
            stemmed = stemmer.stem(lemmatizer.lemmatize(word))
        else:
            stemmed = stemmer.stem(lemmatizer.lemmatize(word, pos=wordnet_tag))
        result.append(stemmed)
    return result
    
def processStopKeywords():
    file_path = "../MODULE_CATALOGUE/module_catalogue_stopwords.csv"
    # convert keywords csv file to dataframe.
    df = pd.read_csv(file_path, index_col=False)['Stopwords']
    preprocessed_stopwords = lemmatize_stem(list(df))
    return set(preprocessed_stopwords)

def module_catalogue_tokenizer(text):
    # Normalization
    text = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text) # replace UCL module codes.
    text = re.sub(r'[/]', " ", text) # separate forward slashes
    text = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', text) # replace numbers.
    text = re.sub(r'[^\w]', " ", text) # remove punctuation.

    # Tokenization
    stopwords = get_stopwords()
    preprocessed_stopwords = processStopKeywords()

    tokens = simple_preprocess(text, min_len=3) # convert text to lowercase tokens
    # remove stopwords
    tokens = [token for token in tokens if token not in stopwords]
    tokens = lemmatize_stem(tokens)
    tokens = [token for token in tokens if token not in preprocessed_stopwords]

    return tokens

def preprocess_text(text):
    tokens = module_catalogue_tokenizer(text)
    return tokens

def preprocess_dataset(dataset):
    return [' '.join(preprocess_text(word)) for word in dataset]

