import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize, bigrams, trigrams
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer
import re

def preprocessText(text):
    # Normalisation
    normalized = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text) # replace UCL module codes.
    normalized = re.sub(r'[/]', " ", normalized) # separate forward slashes
    normalized = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', normalized) # replace numbers.
    normalized = re.sub("[^\w]", " ", normalized) # remove punctuation.

    # Tokenisation
    tokens = word_tokenize(normalized.lower())
    n = len(tokens)

    # Stopword Removal
    stops = set(stopwords.words('english'))
    tokens = [word for word in tokens if not word in stops]

    # Lemmatising and Stemming
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return " ".join(tokens)

def preprocessDataset(dataset):
    n = len(dataset)
    cleaned_dataset = [None] * n
    for i in range(n):
        cleaned_dataset[i] = preprocessText(dataset[i])
    return cleaned_dataset

dataset = [
    "understand the C and Linux/UNIX programming environment, from the hardware (memory hierarchy, memory model between cores) to low-level operating system functionality (file and network I/O, process management, virtual memory system, program linking and loading);",
    "Pre-requisites: ECON0002: Economics, ECON0005: Statistical Methods in Economics, ECON0004: Applied Economics (or equivalents).",
    "Compulsory for 2nd year BSc Economics (L100, L101 and L102) and 3rd year Economics and Statistics (LG13) students. Can be taken by 2nd or 3rd year Economics and Geography (LL17) and Philosophy and Economics (VL51) students, and Mathematics with Economics (G1L1 and G1LC) students."
]

#print(list(bigrams(tokens)))
#print(list(trigrams(tokens)))

cleaned_dataset = preprocessDataset(dataset)


vectorizer = TfidfVectorizer(use_idf=True)
tfidf = vectorizer.fit_transform(cleaned_dataset)
feature_names = vectorizer.get_feature_names()
dense = tfidf.todense()
denselist = dense.tolist()
df = pd.DataFrame(denselist, columns=feature_names)

print(df)