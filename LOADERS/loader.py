import os
import json
import pymongo
import ssl
from bson import json_util

class Loader(): 
    """
        The abstract loader class for loading module/publiction data from serialized JSON files, if they exist, otherwise from MongoDB.
    """

    def __init__(self):
        """
            Initializes connection host and JSON file paths for LDA and SVM prediction results, each containing data for both UCL modules 
            and scopus research publications.
        """
        self.host = "mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        self.lda_prediction_path = "NLP/LDA/SDG_RESULTS/training_results.json"
        self.svm_prediction_path = "NLP/SVM/SDG_RESULTS/training_results.json"

    def load(self, count):
        """
            Loads data from pickled file.
            Returns Pandas DataFrame.
        """
        raise NotImplementedError

    def load_lda_prediction_results(self):
        """
            Loads SDG predictions for LDA from a serialised json file, if it exists, otherwise from MongoDB.
        """
        raise NotImplementedError

    def load_svm_prediction_results(self):
        """
            Loads SDG predictions for Svm from a serialised json file if it exists, otherwise, loads from MongoDB.
        """
        if os.path.exists(self.svm_prediction_path):
            with open(self.svm_prediction_path) as json_file:
                data = json.load(json_file)
        else:
            client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
            db = client.Scopus
            col = db.SvmSdgPredictions
            data = col.find()
            data = json.loads(json_util.dumps(data)) # process mongodb response to a workable dictionary format.
            client.close()

        return data

    def load_string_matches_results(self):
        """
            Loads SDG keyword string matching results from a serialised file, if it exists, otherwise from MongoDB.
        """
        raise NotImplementedError

    def load_pymongo_db(self):
        """
            Downloads data from SQL Server and serialises it into <*.pkl>
        """
        raise NotImplementedError