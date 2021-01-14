import pandas as pd
import pyodbc, re, sys, datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize, bigrams, trigrams
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer

numberOfKeywordsPerDescription = 5
numberOfModulesAnalysed = "MAX" # either MAX in String or an integer

class NLP():
    def __init__(self):
        # SERVER LOGIN DETAILS
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.curr_time = datetime.datetime.now()

        # CONNECT TO DATABASE
        self.myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def get_data(self):
        cur = self.myConnection.cursor()
        numberModules = 1
        if numberOfModulesAnalysed == "MAX":
            # Query into dataframe
            df = pd.read_sql_query("SELECT * FROM [dbo].[ModuleData]", self.myConnection)
            self.myConnection.commit()
            return df
        else:
            # Query into dataframe
            df = pd.read_sql_query("SELECT TOP (%d) * FROM [dbo].[ModuleData]" % int(numberOfModulesAnalysed), self.myConnection)
            self.myConnection.commit()
            return df
        
    def preprocessText(self, text):
        # Normalisation
        normalized = re.sub(r'[A-Z]{4}\d{4}', 'modulecode', text) # replace UCL module codes.
        normalized = re.sub(r'[/]', " ", normalized) # separate forward slashes
        normalized = re.sub(r'[\s]\d+(\.\d+)?[\s]', ' numbr ', normalized) # replace numbers.
        # normalized = re.sub("[^\w]", " ", normalized) # remove punctuation.

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

    def preprocessDataset(self, dataset):
        n = len(dataset)
        cleaned_dataset = [None] * n
        for i in range(n):
            cleaned_dataset[i] = self.preprocessText(dataset[i])
        return cleaned_dataset

    def keywordExtraction(self, dataset, i):
        moduleID = dataset['Module_ID'][i]
        moduleDescription = dataset['Description'][i]
        cleaned_dataset = self.preprocessDataset([moduleDescription])
        cleaned_dataset = [x for x in cleaned_dataset if x]

        if cleaned_dataset:
            vectorizer = TfidfVectorizer(use_idf=True)
            tfidf = vectorizer.fit_transform(cleaned_dataset)
            feature_names = vectorizer.get_feature_names()
            dense = tfidf.todense()
            denselist = dense.tolist()
            df = pd.DataFrame(denselist, columns=feature_names).T
            colName = "Value"
            df.columns = [colName]
            df = df.sort_values(colName, ascending=False)
            return df.head(numberOfKeywordsPerDescription)

    def checkIfExists(self, primaryKey):
        cur = self.myConnection.cursor()
        cur.execute("SELECT * FROM ModuleKeywords WHERE Module_ID = (?)", (primaryKey))
        data = cur.fetchall()
        if len(data) == 0:
            return False
        return True

    def writeData_DB(self, moduleID, keywords):
        cur = self.myConnection.cursor()
        data = []
        freqs = []
        words = []

        if len(keywords) == numberOfKeywordsPerDescription:
            for i in range(len(keywords)):
                value = keywords['Value'][i]
                word = keywords.index.values[i]
                if value > 0.001:
                    words.append(word)
                    freqs.append(value)
            data.append((moduleID, words[0], freqs[0], words[1], freqs[1], words[2], freqs[2], words[3], freqs[3], words[4], freqs[4], self.curr_time))

            # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
            if not data:
                print("Not written --> too many requests")
            else:
                insertion = "INSERT INTO ModuleKeywords(Module_ID, Keyword_1, Frequency_1, Keyword_2, Frequency_2, Keyword_3, Frequency_3, Keyword_4, Frequency_4, Keyword_5, Frequency_5, Last_Updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.executemany(insertion, data)
            self.myConnection.commit()

    def run(self):
        dataset = self.get_data()
        total = len(dataset)
        
        for i in range(total):
            self.progress(i+1, total, "modules -> keyword extraction")
            moduleID = dataset['Module_ID'][i]
            if not self.checkIfExists(moduleID) and dataset['Description'][i]:
                df = self.keywordExtraction(dataset, i)
                self.writeData_DB(moduleID, df)

        self.myConnection.close()
        
obj = NLP()
obj.run()
print("Successfuly written to -> ModuleKeywords")
