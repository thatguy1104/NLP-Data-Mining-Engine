import os
import pandas as pd
import numpy as np
import pyodbc
from itertools import zip_longest

from guided_LDA import GuidedLDA
from preprocess import preprocess_text, preprocess_dataset

'''
X = guidedlda.datasets.load_data(guidedlda.datasets.NYT)
vocab = guidedlda.datasets.load_vocab(guidedlda.datasets.NYT)
word2id = dict((v, idx) for idx, v in enumerate(vocab))

print(X.shape)
print(X.sum)

model = guidedlda.GuidedLDA(n_topics=5, n_iter=100, random_state=7, refresh=20)
model.fit(X)

topic_word = model.topic_word_
n_top_words = 8
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
    print('Topic {}: {}'.format(i, ' '.join(topic_words)))
'''
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
        df = pd.read_sql_query("SELECT Module_ID, Description FROM [dbo].[ModuleData]", myConnection)
        myConnection.commit()
        return df
    else:
        df = pd.read_sql_query("SELECT TOP (%d) Module_ID, Description FROM [dbo].[ModuleData]" % int(numOfModules), myConnection)
        myConnection.commit()
        return df

def preprocess_keyword(keyword):
    return ' '.join(preprocess_text(keyword))

def preprocess_keywords_example():
    seed_topic_list = [['fruit', 'food', 'banana', 'apple juice'],
                        ['sport', 'football', 'basketball', 'bowling'],
                        ['ocean', 'fish']]
    
    for i in range(len(seed_topic_list)):
        seed_topic_list[i] = preprocess_dataset(seed_topic_list[i])

    return seed_topic_list

def preprocess_keywords(file_name):
    # convert keywords csv file to dataframe.
    os.chdir("./MODULE_CATALOGUE/INITIALISER/SDG_KEYWORDS")
    current_dir = os.getcwd()
    
    file_path = os.path.join(current_dir, file_name)
    df = pd.read_csv(file_path)

    os.chdir(tempDir)

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

def load_dataset(numOfModules):
    data = getDBTable(numOfModules)
    data = data.dropna()
    return pd.DataFrame(data=data, columns=["Module_ID", "Description"])

def run_example():
    keywords = preprocess_keywords_example()
    data = load_dataset_example()
    iterations = 100

    lda = GuidedLDA(data, keywords, iterations)
    lda.train()
    lda.display_document_topic_words(6)

def run():
    keywords = preprocess_keywords("SDG_Keywords.csv")
    data = load_dataset(1000)
    iterations = 100

    lda = GuidedLDA(data, keywords, iterations)
    lda.train()
    lda.display_document_topic_words(6)

run()
