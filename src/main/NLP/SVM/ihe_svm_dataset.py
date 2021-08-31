import pyodbc
import datetime
import pandas as pd
import numpy as np
import json
import sys
import pymongo
from bson import json_util

from main.LOADERS.module_loader import ModuleLoader
from main.LOADERS.publication_loader import PublicationLoader
from main.NLP.PREPROCESSING.preprocessor import Preprocessor
from main.NLP.PREPROCESSING.module_preprocessor import ModuleCataloguePreprocessor


class IheSvmDataset():
    """
        Creates UCL modules and Scopus research publications dataset with SDG tags for training the SVM.
        The dataset is a dataframe with columns {ID, Description, SDG} where ID is either Module_ID or DOI.
    """

    def __init__(self):
        """
            Initializes the threshold for tagging a document with an SDG, module loader, publication loader and output pickle file.
        """
        self.threshold = 30  # threshold value for tagging a document with an SDG, for a probability greater than this value.
        self.publication_loader = PublicationLoader()
        self.publication_preprocessor = Preprocessor()
        self.svm_dataset = "main/NLP/SVM/SVM_dataset_ihe.csv"

        with open("main/NLP/LDA/IHE_RESULTS/training_results.json") as json_file:
           self.data = json.load(json_file)

        # dataframe with columns {DOI, Title, Description}.
        self.df_publications = self.publication_loader.load("MAX")
        self.num_ihes = len(self.data['Topic Words'])

    def __progress(self, count: int, total: int, custom_text: str, suffix: str = '') -> None:
        """
            Visualises progress for a process given a current count and a total count.
        """
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %
                         (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def get_publication_description(self, doi: str):
        """
            Returns the publication description for a particular DOI.
        """

        # search for row in dataframe by DOI.
        df = self.df_publications.loc[self.df_publications["DOI"] == doi]
        return None if len(df) == 0 else df["Description"].values[0]

    def tag_publications(self) -> pd.DataFrame:
        """
            Returns a dataframe with columns {ID, Description, SDG} for each publication, where SDG is a class tag for training the SVM.
        """
        results = pd.DataFrame(columns=['ID', 'Description', 'IHE'])  # ID = DOI
        
        num_publications = len(self.data['Document Topics'])
        final_data = {}
        counter = 0

        for doi in self.data['Document Topics']:
            self.__progress(counter, num_publications, "Forming Publications IHE Dataset for SVM...")
            raw_weights = self.data['Document Topics'][doi]
            weights = [0] * self.num_ihes
            for i in range(self.num_ihes):
                ihe_num = str(i + 1)
                weight = raw_weights[i][4:-2]
                try:
                    # convert probabilities in the range [0,1] to percentages.
                    w = float(weight)
                except:
                    w = 0.0
                weights[i] = w
            
            weights = np.asarray(weights)
            # gets SDG corresponding to the maximum weight.
            ihe_max = weights.argmax() + 1
            ihe_weight_max = weights[ihe_max - 1]  # gets the maximum weight.

            description = self.get_publication_description(doi)
            description = "" if description is None else self.publication_preprocessor.preprocess(description)

            if description != "":
                if ihe_weight_max >= self.threshold:
                    # Set SDG tag of publication to the SDG which has the maximum weight if its greater than the threshold value.
                    row_df = pd.DataFrame([[doi, description, ihe_max]], columns=results.columns)
                else:
                    # Set SDG tag of module to None if the maximum weight is less than the threshold value.
                    row_df = pd.DataFrame([[doi, description, None]], columns=results.columns)

                results = results.append(row_df, verify_integrity=True, ignore_index=True)

            counter += 1
        print()
        return results

    def run(self) -> None:
        """
            Tags the modules and/or publications with their most related SDG, if related to one at all, and combines them into a single dataframe.
            Serializes the resulting dataframe as a pickle file.
        """
        df = pd.DataFrame()  # column format of dataframe is {ID, Description, SDG} where ID is either Module_ID or DOI.
        df = df.append(self.tag_publications(), ignore_index=True)

        df = df.reset_index()
        df.to_csv(self.svm_dataset)
