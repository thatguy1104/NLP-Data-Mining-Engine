
import os
import pandas as pd

from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS as gensim_stopwords

from nltk import bigrams, trigrams, pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet, stopwords as nltk_stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import re 

def get_stopwords():
    nltk_stopwords_set = set(nltk_stopwords.words('english'))
    module_catalogue_stopwords = preprocess_module_catalogue_stopwords()
    stopwords = nltk_stopwords_set.union(module_catalogue_stopwords)
    return gensim_stopwords.union(stopwords)

def get_wordnet_pos(word):
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def text_lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    text = lemmatizer.lemmatize(text, pos=get_wordnet_pos(text))
    return text
    
def preprocess_module_catalogue_stopwords():
    tempcwd = os.getcwd()
    os.chdir("../MODULE_CATALOGUE")    
    file_path = os.path.join(os.getcwd(), "module_catalogue_stopwords.csv")
    df = pd.read_csv(file_path, index_col=False)['Stopwords']
    os.chdir(tempcwd)
    preprocessed_stopwords = [text_lemmatizer(w) for w in list(df)] 
    return set(preprocessed_stopwords)

def module_catalogue_tokenizer(text):
    # Normalization
    text = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text) # replace UCL module codes.
    text = re.sub(r'[/]', " ", text) # separate forward slashes
    text = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', text) # replace numbers.
    text = re.sub(r'[^\w]', " ", text) # remove punctuation.

    # Stopwords
    stopwords = get_stopwords()
    
    # Tokenization
    text = text.lower()
    tokens = [word for word in word_tokenize(text)]
    tokens = [word for word in tokens if len(word) >= 4]
    tokens = [text_lemmatizer(t) for t in tokens]
    tokens = [t for t in tokens if t not in stopwords]

    return tokens

def preprocess_text(text):
    tokens = module_catalogue_tokenizer(text)
    return tokens

def preprocess_dataset(dataset):
    return [' '.join(preprocess_text(word)) for word in dataset]
