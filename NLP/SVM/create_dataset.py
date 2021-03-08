import pyodbc
import datetime
import pandas as pd
import json
import sys

# SERVER LOGIN DETAILS
server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'
curr_time = datetime.datetime.now()

# CONNECT TO DATABASE
myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
threshold = 20

def progress(count, total, custom_text, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '*' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
    sys.stdout.flush()

def get_description(moduleID):
    cur = myConnection.cursor()
    cur.execute("SELECT Description FROM ModuleData WHERE Module_ID = (?)", (moduleID))
    data = cur.fetchall()
    return "" if len(data) == 0 else data

def process_modules():
    results = pd.DataFrame(columns=['ModuleID', 'Description', 'SDG'])
    with open('NLP/MODEL_RESULTS/training_results.json') as json_file:
        data = json.load(json_file)
        doc_topics = data['Document Topics']
        final_data = {}
        counter = 0
        for module in doc_topics:
            progress(counter, len(doc_topics), "Forming UCL Module Dataset for SVM...")
            raw_weights = doc_topics[module]
            weights = []
            for i in range(len(raw_weights)):
                raw_weights[i] = raw_weights[i].replace('(', '').replace(')', '').replace('%', '').replace(' ', '').split(',')
                sdg_num = int(raw_weights[i][0])
                try:
                    w = float(raw_weights[i][1])
                except:
                    w = 0.0
                weights.append((sdg_num, w))

            sdg_weight_max = max(weights, key=lambda x: x[1]) # get (sdg, weight) with the maximum weight.

            if sdg_weight_max[1] >= threshold:
                row_dataframe = pd.DataFrame([[module, get_description(module)[0][0], sdg_weight_max[0]]], columns=results.columns)
            else:
                row_dataframe = pd.DataFrame([[module, get_description(module)[0][0], None]], columns=results.columns)
            results = results.append(row_dataframe, verify_integrity=True, ignore_index=True)
            counter += 1
    
    return results

def process_publications():
    return None # TODO: implement me

def run(create_modules, create_publications):
    df = pd.DataFrame()
    if create_modules:
        df.append(process_modules())
    if create_publications:
        df.append(process_publications())

    #df.to_pickle("NLP/SVM/SVM_dataset.pkl")
    print(df)

run(True, False)