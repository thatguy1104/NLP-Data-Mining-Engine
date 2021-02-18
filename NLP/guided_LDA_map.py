import os, sys, time, datetime
import pandas as pd
import numpy as np
import pyodbc
from itertools import zip_longest

from guided_LDA import GuidedLDA
from preprocess import module_catalogue_tokenizer

def progress(count, total, custom_text, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '*' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
    sys.stdout.flush()

def getDBTable(numOfModules):
    # SERVER LOGIN DETAILS
    server = 'miemie.database.windows.net'
    database = 'MainDB'
    username = 'miemie_login'
    password = 'e_Paswrd?!'
    driver = '{ODBC Driver 17 for SQL Server}'
    # CONNECT TO DATABASE
    myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    if numOfModules == "MAX":
        df = pd.read_sql_query("SELECT Module_Name, Module_ID, Description FROM [dbo].[ModuleData]", myConnection)
        myConnection.commit()
        return df
    else:
        df = pd.read_sql_query("SELECT TOP (%d) Module_Name, Module_ID, Description FROM [dbo].[ModuleData]" % int(numOfModules), myConnection)
        myConnection.commit()
        return df

def preprocess_keywords_example():
    seed_topic_list = [['fruit', 'food', 'banana', 'apple juice'],
                        ['sport', 'football', 'basketball', 'bowling'],
                        ['ocean', 'fish']]
    for i in range(len(seed_topic_list)):
        seed_topic_list[i] = [' '.join(module_catalogue_tokenizer(w)) for w in seed_topic_list[i]]
    return seed_topic_list

def preprocess_keyword(keyword):
    return ' '.join(module_catalogue_tokenizer(keyword))

def preprocess_keywords(file_name):
    # convert keywords csv file to dataframe.
    tempcwd = os.getcwd()
    os.chdir("../COMP0016_2020_21_Team16/MODULE_CATALOGUE/SDG_KEYWORDS") #os.chdir("../MODULE_CATALOGUE/SDG_KEYWORDS")
    file_path = os.path.join(os.getcwd(), file_name)
    df = pd.read_csv(file_path)
    os.chdir(tempcwd)

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
    for keywords in preprocess_keywords("SDG_Keywords.csv"):
        print(keywords)
        print()

def load_dataset_example():
    data = [
        "I like fruit such as banana, apple and orange.", # food
        "The football match was a great game! I like the sports football, basketball and cricket.", # sports
        "This morning I made a smoothie with banana, apple juice and kiwi.", # food
        "The ocean is warm and the fish were swimming. I want to go snorkeling tomorrow and play football on the beach" # ocean
    ]
    return pd.DataFrame(data=data, columns=["Description"])

def moduleHasKeyword(data, df):
    indicies = []
    counter = 1
    length = len(data)

    for i in range(length):  # iterate through the paper descriptions
        progress(counter, length, "processing for guidedLDA")
        moduleName = data["Module_Name"][i]
        if data["Description"][i]:
            description = data["Description"][i]
        else:
            description = ""
        textData = moduleName + " " + description

        text = module_catalogue_tokenizer(textData)
        for p in df:  # iterate through SDGs
            found = 0
            for j in df[p]: # iterate through the keyword in p SDG
                temp = j
                word = module_catalogue_tokenizer(j)
                " ".join(text)
                " ".join(word)
                if word in text:
                    found += 1
            if found == 0:
                indicies.append(i)
        counter += 1
    
    print()
    data.drop(indicies)
    return data

def moduleHasKeywordJSON(data):
    indicies = []
    #dataJSON = pd.read_json('../MODULE_CATALOGUE/matchedModulesSDG.json')
    dataJSON = pd.read_json("../COMP0016_2020_21_Team16/MODULE_CATALOGUE/matchedModulesSDG.json")
    for p in dataJSON:
        listSDG = dataJSON[p]['Related_SDG']
        if len(listSDG) == 0:
            indicies.append(p)

    for i in indicies:
        data = data[data.Module_ID != i]
    return data

def load_dataset(numOfModules):
    tempCwd = os.getcwd()
    os.chdir("../COMP0016_2020_21_Team16/MODULE_CATALOGUE/SDG_KEYWORDS") #os.chdir("../MODULE_CATALOGUE/SDG_KEYWORDS")
    file_path = os.path.join(os.getcwd(), "SDG_Keywords.csv")
    df = pd.read_csv(file_path)
    os.chdir(tempCwd)

    df = df.dropna()
    data = getDBTable(numOfModules)
    data = data.dropna()

    return pd.DataFrame(data=moduleHasKeywordJSON(data), columns=["Module_ID", "Description"])

def run_example():
    keywords = preprocess_keywords_example()
    data = load_dataset_example()
    iterations = 100
    seed_confidence = 1.0

    lda = GuidedLDA(data, keywords, iterations)
    lda.train(seed_confidence)
    lda.display_document_topic_words(6)

def run():
    ts = time.time()
    startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    keywords = preprocess_keywords("SDG_Keywords.csv")
    numberOfModules = "MAX"
    data = load_dataset(numberOfModules)
    iterations = 1000
    seed_confidence = 1.0

    lda = GuidedLDA(data, keywords, iterations)
    lda.train(seed_confidence)
    lda.display_document_topic_words(20)

    print("Size before/after filtering -->",  str(numberOfModules), "/", len(data))

run()
#run_example()
