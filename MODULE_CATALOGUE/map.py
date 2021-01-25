import os, sys, re
import json
import pyodbc
import datetime
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

numberOfModulesAnalysed = "MAX"

# SERVER LOGIN DETAILS
server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'
curr_time = datetime.datetime.now()

# CONNECT TO DATABASE
myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server +';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

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
    cur = myConnection.cursor()
    numberModules = 1
    if numberOfModulesAnalysed == "MAX":
        # Query into dataframe
        df = pd.read_sql_query("SELECT * FROM [dbo].[ModuleData]", myConnection)
        myConnection.commit()
        return df
    else:
        # Query into dataframe
        df = pd.read_sql_query("SELECT TOP (%d) * FROM [dbo].[ModuleData]" % int(numberOfModulesAnalysed), myConnection)
        myConnection.commit()
        return df

def readKeywords(data):
    fileName = "SDG_Keywords.csv"
    # SDG keyword data
    df = pd.read_csv(fileName)
    df = df.dropna()
    resulting_data = {}
    counter = 0
    length = len(data)

    # # Reset the data file
    if os.path.exists("matchedModulesSDG.json"):
        os.remove("matchedModulesSDG.json")

    for i in range(length):  # iterate through the paper descriptions
        progress(counter, length, "processing matchedModulesSDG.json")
        counter += 1
        moduleName = data["Module_Name"][i]
        if data["Description"][i]:
            description = data["Description"][i]
        else:
            description = ""
        textData = moduleName + " " + description

        sdg_occurences = {}
        for p in df:  # iterate through SDGs
            sdg_occurences[p] = {"Word_Found": []}
            for j in df[p]:
                text = preprocessText(textData)
                word = preprocessText(j)
                if word in text:
                    sdg_occurences[p]["Word_Found"].append(j)
            if len(sdg_occurences[p]["Word_Found"]) == 0:
                del sdg_occurences[p]
            resulting_data[data["Module_ID"][i]] = {"Module_Name": data["Module_Name"][i], "Related_SDG": sdg_occurences}
    print()
    with open('matchedModulesSDG.json', 'a') as outfile:
        json.dump(resulting_data, outfile)


data = getFileData()
readKeywords(data)
