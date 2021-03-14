import pyodbc
import datetime
import pandas as pd
import numpy as np
import json
import sys
import pymongo
from bson import json_util

from NLP.LDA.predict_publication import ScopusPrediction

class SVMDataset():
    def __init__(self):
        # SERVER LOGIN DETAILS
        server = 'miemie.database.windows.net'
        database = 'MainDB'
        username = 'miemie_login'
        password = 'e_Paswrd?!'
        driver = '{ODBC Driver 17 for SQL Server}'
        curr_time = datetime.datetime.now()

        # CONNECT TO DATABASE
        self.myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        self.threshold = 20
        
        self.scopus_map = ScopusMap()

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def get_module_description(self, module_id):
        cur = self.myConnection.cursor()
        cur.execute("SELECT Description FROM ModuleData WHERE Module_ID = (?)", (module_id))
        data = cur.fetchall()
        return None if len(data) == 0 else data

    def get_publication_description(self, doi):
        df = self.scopus_map.publiction_data
        df = df.loc[df["DOI"] == doi]
        return None if len(df) == 0 else df["Description"].values[0]

        #file_name = doi + ".json"
        #df = self.scopus_map.load_publication(file_name)
        #return df["Description"]
    
    def process_modules(self):
        results = pd.DataFrame(columns=['ID', 'Description', 'SDG']) # ID = ModuleID
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.ModulePrediction
        data = col.find()
        
        for elements in data:
        # with open('NLP/MODEL_RESULTS/training_results.json') as json_file:
        #     data = json.load(json_file)
            elements = json.loads(json_util.dumps(elements))
            doc_topics = elements['Document Topics']
            num_modules = len(doc_topics)
            final_data = {}
            counter = 0
            for module in doc_topics:
                self.progress(counter, num_modules, "Forming Modules Dataset for SVM...")
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

                if sdg_weight_max[1] >= self.threshold:
                    row_df = pd.DataFrame([[module, self.get_module_description(module)[0][0], sdg_weight_max[0]]], columns=results.columns)
                else:
                    row_df = pd.DataFrame([[module, self.get_module_description(module)[0][0], None]], columns=results.columns)
                results = results.append(row_df, verify_integrity=True, ignore_index=True)
                counter += 1
        client.close()
        return results

    def process_publications(self):
        print("Loading publications...")
        self.scopus_map.load_publications()
        print("Finished.")

        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.PublicationPrediction
        data = col.find()

        results = pd.DataFrame(columns=['ID', 'Description', 'SDG']) # ID = DOI

        # with open('NLP/MODEL_RESULTS/scopus_prediction_results.json') as json_file:
        #     data = json.load(json_file)

        num_publications = data.count()
        final_data = {}
        counter = 0
        for doi in data:
            self.progress(counter, num_publications,"Forming Publications Dataset for SVM...")
            raw_weights = data[doi]
            num_sdgs = len(raw_weights) - 1 # subtract the title.
            weights = [0] * num_sdgs
            for i in range(num_sdgs):
                sdg_num = str(i + 1)
                try:
                    w = float(raw_weights[sdg_num]) * 100.0
                except:
                    w = 0.0
                weights[i] = w
        
            weights = np.asarray(weights)
            sdg_max = weights.argmax() + 1 # SDG with maximum weight.
            sdg_weight_max = weights[sdg_max - 1] # maximum weight.
            
            if sdg_weight_max >= self.threshold:
                row_df = pd.DataFrame([[doi, self.get_publication_description(doi), sdg_max]], columns=results.columns)
            else:
                row_df = pd.DataFrame([[doi, self.get_publication_description(doi), None]], columns=results.columns)
            results = results.append(row_df, verify_integrity=True, ignore_index=True)
            counter += 1

        return results

    def run(self, modules, publications):
        df = pd.DataFrame()
        if modules:
            df = df.append(self.process_modules())
        if publications:
            df = df.append(self.process_publications())

        df.to_pickle("NLP/SVM/SVM_dataset.pkl")
