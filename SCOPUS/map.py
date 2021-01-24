import os, sys, re
import json
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def progress(count, total, custom_text, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '*' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s %s\r' %
                     (bar, percents, '%', custom_text, suffix))
    sys.stdout.flush()

def preprocessText(text):
    # Normalisation
    # replace UCL module codes.
    normalized = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text)
    normalized = re.sub(r'[/]', " ", normalized)  # separate forward slashes
    # replace numbers.
    normalized = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', normalized)
    normalized = re.sub("[^\w]", " ", normalized)  # remove punctuation.

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

def getFileData():
    files_directory = "GENERATED_FILES/"
    DIR = 'GENERATED_FILES'
    num_of_files = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

    resulting_data = {}
    for i in range(1, num_of_files):
        with open(files_directory + str(i) + ".json") as json_file:
            data = json.load(json_file)
            if data and data["Abstract"] and data["DOI"]:
                abstract = data["Abstract"]
                title = data["Title"]
                doi = data["DOI"]
                if data["AuthorKeywords"]:
                    authorKeywords = data["AuthorKeywords"]
                else:
                    authorKeywords = None
                if data["IndexKeywords"]:
                    indexKeywords = data["IndexKeywords"]
                else:
                    indexKeywords = None
                resulting_data[doi] = {"Title" : title, "DOI" : doi, "Abstract" : abstract, "AuthorKeywords" : authorKeywords, "IndexKeywords" : indexKeywords}
    return resulting_data

def readKeywords(data):
    fileName = "SDG_Keywords.csv"
    # SDG keyword data
    df = pd.read_csv(fileName)
    df = df.dropna()
    resulting_data = {}
    counter = 0
    length = len(data)

    # Reset the data file
    if os.path.exists("matchedScopusSDG.json"):
        os.remove("matchedScopusSDG.json")

    for i in data: # iterate through the paper descriptions
        progress(counter, length, "processing matchedScopusSDG.json")
        counter += 1
        textData = data[i]["Title"] + " " + data[i]["Abstract"]
        if data[i]["AuthorKeywords"]:
            for j in data[i]["AuthorKeywords"]:
                textData += " " + j
        if data[i]["IndexKeywords"]:
            for j in data[i]["IndexKeywords"]:
                textData += " " + j
        
        sdg_occurences = {}
        for p in df: # iterate through SDGs
            for j in df[p]:
                text = preprocessText(textData)
                word = preprocessText(j)
                if word in text:
                    sdg_occurences[p] = {"Word_Found" : j}
            resulting_data[data[i]["DOI"]] = {"PublicationInfo" : data[i], "Related_SDG" : sdg_occurences}
    print()
    with open('matchedScopusSDG.json', 'a') as outfile:
        json.dump(resulting_data, outfile)
        

data = getFileData()
readKeywords(data)