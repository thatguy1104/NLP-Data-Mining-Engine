import pyodbc
import datetime
import pandas as pd
import numpy as np
import json
import sys
import pymongo
from bson import json_util

from LOADERS.module_loader import ModuleLoader
from LOADERS.publication_loader import PublicationLoader

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
        
        self.module_loader = ModuleLoader()
        self.publication_loader = PublicationLoader()
        self.svm_dataset = "NLP/SVM/SVM_dataset.pkl"

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def get_module_description(self, module_id):
        df = self.module_loader.load("MAX")
        df = df.loc[df["Module_ID"] == module_id]
        return None if len(df) == 0 else df["Description"].values[0]

    def get_publication_description(self, doi):
        df = self.publication_loader.load("MAX")
        df = df.loc[df["DOI"] == doi]
        return None if len(df) == 0 else df["Description"].values[0]
    
    def process_modules(self):
        results = pd.DataFrame(columns=['ID', 'Description', 'SDG']) # ID = ModuleID
        data = self.module_loader.load_prediction_results()

        for module in data:
            module = json.loads(json_util.dumps(module))
            doc_topics = module['Document Topics']
            num_modules = len(doc_topics)
            final_data = {}
            counter = 0
            for module_id in doc_topics:
                self.progress(counter, num_modules, "Forming Modules Dataset for SVM...")
                raw_weights = doc_topics[module_id]
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
                    row_df = pd.DataFrame([[module_id, self.get_module_description(module_id)[0][0], sdg_weight_max[0]]], columns=results.columns)
                else:
                    row_df = pd.DataFrame([[module_id, self.get_module_description(module_id)[0][0], None]], columns=results.columns)
                results = results.append(row_df, verify_integrity=True, ignore_index=True)
                counter += 1
                
        return results

    def process_publications(self):
        results = pd.DataFrame(columns=['ID', 'Description', 'SDG']) # ID = DOI
        data = self.publication_loader.load_prediction_results()

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

        df.to_pickle(self.svm_dataset)