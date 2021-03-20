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

class SdgSvmDataset():
    """
        Creates UCL modules and Scopus research publications dataset with SDG tags for training the SVM.
        The dataset is a dataframe with columns {ID, Description, SDG} where ID is either Module_ID or DOI.
    """

    def __init__(self):
        """
            Initializes the threshold for tagging a document with an SDG, module loader, publication loader and output pickle file.
        """
        self.threshold = 20 # threshold value for tagging a document with an SDG, for a probability greater than this value.
        self.module_loader = ModuleLoader()
        self.publication_loader = PublicationLoader()
        self.svm_dataset = "NLP/SVM/SVM_dataset.pkl"

    def __progress(self, count: int, total: int, custom_text: str, suffix: str ='') -> None:
        """
            Visualises progress for a process given a current count and a total count.
        """
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def get_module_description(self, module_id: str):
        """
            Returns the module description for a particular module_id.
        """
        df = self.module_loader.load("MAX") # dataframe with columns {Module_ID, Description}.
        df = df.loc[df["Module_ID"] == module_id] # search for row in dataframe by Module_ID.
        return None if len(df) == 0 else df["Description"].values[0]

    def get_publication_description(self, doi: str):
        """
            Returns the publication description for a particular DOI.
        """
        df = self.publication_loader.load("MAX") # dataframe with columns {DOI, Title, Description}. 
        df = df.loc[df["DOI"] == doi] # search for row in dataframe by DOI.
        return None if len(df) == 0 else df["Description"].values[0]
    
    def tag_modules(self):
        """
            Returns a dataframe with columns {ID, Description, SDG} for each module, where SDG is a class tag for training the SVM.
        """
        results = pd.DataFrame(columns=['ID', 'Description', 'SDG']) # ID = Module_ID
        data = self.module_loader.load_prediction_results() # loads data from the ModulePrediction table in mongodb.
        data = json.loads(json_util.dumps(data))
        # del data['_id']

        doc_topics = data['Document Topics']
        num_modules = len(doc_topics)
        final_data = {}
        counter = 0
        for module_id in doc_topics:
            self.__progress(counter, num_modules, "Forming Modules Dataset for SVM...")
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

            sdg_weight_max = max(weights, key=lambda x: x[1]) # get tuple (sdg, weight) with the maximum weight.

            if sdg_weight_max[1] >= self.threshold:
                # Set SDG tag of module to the SDG which has the maximum weight if its greater than the threshold value.
                row_df = pd.DataFrame([[module_id, self.get_module_description(module_id), sdg_weight_max[0]]], columns=results.columns)
            else:
                # Set SDG tag of module to None if the maximum weight is less than the threshold value.
                row_df = pd.DataFrame([[module_id, self.get_module_description(module_id), None]], columns=results.columns)
            
            results = results.append(row_df, verify_integrity=True, ignore_index=True)
            counter += 1
                
        return results

    def tag_publications(self):
        """
            Returns a dataframe with columns {ID, Description, SDG} for each publication, where SDG is a class tag for training the SVM.
        """
        results = pd.DataFrame(columns=['ID', 'Description', 'SDG']) # ID = DOI
        data = self.publication_loader.load_prediction_results() # loads data from the PublicationPrediction table in mongodb.
        data = json.loads(json_util.dumps(data))

        num_publications = len(data)
        final_data = {}
        counter = 0

        for doi in data:
            print(doi)
            del doi['_id']

            self.__progress(counter, num_publications, "Forming Publications Dataset for SVM...")
            raw_weights = data[doi]
            num_sdgs = len(raw_weights) - 1 # subtract the title.
            weights = [0] * num_sdgs
            for i in range(num_sdgs):
                sdg_num = str(i + 1)
                try:
                    w = float(raw_weights[sdg_num]) * 100.0 # convert probabilities in the range [0,1] to percentages.
                except:
                    w = 0.0
                weights[i] = w
            
            weights = np.asarray(weights)
            sdg_max = weights.argmax() + 1 # gets SDG corresponding to the maximum weight.
            sdg_weight_max = weights[sdg_max - 1] # gets the maximum weight.
            
            if sdg_weight_max >= self.threshold:
                # Set SDG tag of publication to the SDG which has the maximum weight if its greater than the threshold value.
                row_df = pd.DataFrame([[doi, self.get_publication_description(doi), sdg_max]], columns=results.columns)
            else:
                # Set SDG tag of module to None if the maximum weight is less than the threshold value.
                row_df = pd.DataFrame([[doi, self.get_publication_description(doi), None]], columns=results.columns)
            
            results = results.append(row_df, verify_integrity=True, ignore_index=True)
            counter += 1

        return results

    def run(self, modules: bool, publications: bool):
        """
            Tags the modules and/or publications with their most related SDG, if related to one at all, and combines them into a single dataframe.
            Serializes the resulting dataframe as a pickle file.
        """
        df = pd.DataFrame() # column format of dataframe is {ID, Description, SDG} where ID is either Module_ID or DOI.
        # if modules:
        #     df = df.append(self.tag_modules())
        if publications:
            df = df.append(self.tag_publications(), verify_integrity=True, ignore_index=True)

        # df.to_pickle(self.svm_dataset)
        print(df.head(100))