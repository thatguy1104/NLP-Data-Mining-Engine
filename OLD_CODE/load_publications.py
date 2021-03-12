import pymongo
from bson import json_util

class LoadPublications():
    def load(self):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.Data
        data = col.find()
        return data