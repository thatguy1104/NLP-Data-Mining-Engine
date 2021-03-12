import pymongo
from bson import json_util


class LoadPublications():
    def __init__(self):
        self.data = None
    def load(self):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.Data
        results = col.find()
        self.data = results
        client.close()
        return self.data
        