import pandas as pd
import pyodbc, re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize, bigrams, trigrams
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer

numberOfKeywordsPerDescription = 5
numberOfModulesAnalysed = 3

class NLP():
    def __init__(self):
        # SERVER LOGIN DETAILS
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'

    def get_data(self):
        # CONNECT TO DATABASE
        myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        cur = myConnection.cursor()

        # Query into dataframe
        df = pd.read_sql_query("SELECT TOP (%d) * FROM [dbo].[ModuleData]" % numberOfModulesAnalysed, myConnection)

        myConnection.commit()
        myConnection.close()
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

    def run(self):
        dataset = self.get_data()
        
        for i in range(len(dataset)):
            moduleID = dataset['Module_ID'][i]
            moduleDescription = dataset['Description'][i]
            cleaned_dataset = self.preprocessDataset([moduleDescription])
            vectorizer = TfidfVectorizer(use_idf=True)
            tfidf = vectorizer.fit_transform(cleaned_dataset)
            feature_names = vectorizer.get_feature_names()
            dense = tfidf.todense()
            denselist = dense.tolist()
            df = pd.DataFrame(denselist, columns=feature_names).T
            colName = "Value"
            df.columns = [colName]
            df = df.sort_values(colName, ascending=False)
            print("ID ", moduleID)
            print("DESC ", moduleDescription)
            print(df.head(numberOfKeywordsPerDescription))
            print()

obj = NLP()
obj.run()