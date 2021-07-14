import sys
import pymongo
import ssl

class MongoDbPusher():
    def __init__(self):
        self.host = "mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

    def progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()
        
    def ihe_prediction(self, data: dict) -> None:
        """
            Update IHE model prediction cluster
            MongoDB cluster - IHEPrediction
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.IHEPrediction
        col.drop()
        key = value = data
        col.update_one(data, {"$set": value}, upsert=True)
        client.close()

    def module_prediction(self, data) -> None:
        """
            Update Module model prediction cluster 
            MongoDB cluster - ModulePrediction
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.ModulePrediction
        col.drop()
        key = value = data
        col.update_one(data, {"$set": value}, upsert=True)
        client.close()

    def matched_modules(self, data: dict) -> None:
        """
            Update module string matching cluster
            MongoDB cluster - MatchedModules
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.MatchedModules
        col.drop()
        data_len = len(data)
        counter = 1
        for key in data:
            self.progress(counter, data_len, "Uploading MatchedModules to MongoDB")
            value = data[key]
            col.update_one({"Module_ID": key}, {"$set": value}, upsert=True)
            counter += 1
        client.close()

    def matched_scopus(self, data: dict) -> None:
        """
            Update publication string matching cluster
            MongoDB cluster - 
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.MatchedScopus
        col.drop()
        data_len = len(data)
        counter = 1
        for i in data:
            self.progress(counter, data_len, "Uploading MatchedScopus to MongoDB")
            key = data[i]["DOI"]
            value = data[i]
            col.update_one({"DOI": key}, {"$set": value}, upsert=True)
            counter += 1
        client.close()

    def module_validation(self, data) -> None:
        """
            Update module validation cluster
            MongoDB cluster - ModuleValidation
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.ModuleValidation
        key = value = data
        col.update(key, value, upsert=True)
        client.close()

    def scopus_validation(self, data) -> None:
        """
            Update scopus validation cluster
            MongoDB cluster - ScopusValidation
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.ScopusValidation
        key = value = data
        col.update(key, value, upsert=True)
        client.close()

    def svm_sdg_predictions(self, data) -> None:
        """
            Update SDG predictions using SVM on modules and publications. 
            MongoDB cluster - SvmSdgPredictions
        """
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.SvmSdgPredictions
        key = value = data
        col.update(key, value, upsert=True)
        client.close()