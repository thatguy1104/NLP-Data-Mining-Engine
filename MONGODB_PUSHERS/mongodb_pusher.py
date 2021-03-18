import sys
import pymongo
import ssl

class MongoDbPusher():
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
        self.db = self.client.Scopus

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()
        
    def ihe_prediction(self, data):
        col = self.db.IHEPrediction
        col.drop()
        key = value = data
        col.update_one(data, {"$set": value}, upsert=True)
        self.client.close()

    def module_prediction(self, data):
        col = self.db.ModulePrediction
        col.drop()
        key = value = data
        col.update_one(data, {"$set": value}, upsert=True)
        self.client.close()

    def matched_modules(self, data):
        col = self.db.MatchedModules
        col.drop()
        data_len = len(data)
        counter = 1
        for i in data:
            self.progress(counter, data_len, "Uploading MatchedModules to MongoDB")
            value = data[i]
            col.update_one({"Module_ID": i}, {"$set": value}, upsert=True)
        self.client.close()

    def matched_scopus(self, data):
        col = self.db.MatchedScopus
        col.drop()
        data_len = len(data)
        counter = 1
        for i in data:
            self.progress(counter, data_len, "Uploading MatchedScopus to MongoDB")
            key = data[i]["DOI"]
            value = data[i]
            col.update_one({"DOI": key}, {"$set": value}, upsert=True)
            counter += 1
        self.client.close()
