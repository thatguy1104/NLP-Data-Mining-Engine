import os, sys, re
import json
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class ScopusMap():

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' %
                        (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def preprocessText(self, text):
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

    def getFileData(self):
        files_directory = "SCOPUS/GENERATED_FILES/"
        resulting_data = {}
        allFileNames = os.listdir(files_directory)
        for i in allFileNames:
            with open(files_directory + i) as json_file:
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

    def readKeywords(self,data):
        fileName = "SDG_Keywords.csv"
        # SDG keyword data
        df = pd.read_csv(fileName)
        df = df.dropna()
        resulting_data = {}
        counter = 0
        length = len(data)

        # Reset the data file
        if os.path.exists("SCOPUS/matchedScopusSDG.json"):
            os.remove("SCOPUS/matchedScopusSDG.json")

        occuringWordCount = {}
        for p in df:  # iterate through SDGs
            occuringWordCount[p] = {}
            for j in df[p]:
                occuringWordCount[p][j] = 0

        for i in data: # iterate through the paper descriptions
            self.progress(counter, length, "processing SCOPUS/matchedScopusSDG.json")
            counter += 1
            textData = data[i]["Title"] + " " + data[i]["Abstract"]
            if data[i]["AuthorKeywords"]:
                for j in data[i]["AuthorKeywords"]:
                    textData += " " + j
            if data[i]["IndexKeywords"]:
                for j in data[i]["IndexKeywords"]:
                    textData += " " + j
            
            sdg_occurences = {}
            sdg_occurences = {}
            for p in df:  # iterate through SDGs
                sdg_occurences[p] = {"Word_Found": []}
                for j in df[p]:
                    text = self.preprocessText(textData)
                    word = self.preprocessText(j)
                    if word in text:
                        occuringWordCount[p][j] += 1
                        sdg_occurences[p]["Word_Found"].append(j)
                if len(sdg_occurences[p]["Word_Found"]) == 0:
                    del sdg_occurences[p]
                resulting_data[data[i]["DOI"]] = {"PublicationInfo" : data[i], "Related_SDG" : sdg_occurences}
        print()
        with open('SCOPUS/matchedScopusSDG.json', 'a') as outfile:
            json.dump(resulting_data, outfile)
        with open('SCOPUS/sdgCount.json', 'w') as outfile:
            json.dump(occuringWordCount, outfile)

    def run(self):
        data = self.getFileData()
        self.readKeywords(data)
