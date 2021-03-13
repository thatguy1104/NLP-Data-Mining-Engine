import pymongo
import json
from LOADERS.loader import Loader
import pandas as pd

class PublicationLoader(Loader):
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db = client.Scopus
        self.col = db.Data

    def load(self):
        data = self.col.find()
        return data

    def load(self, count):
        data = self.col.find().limit(count)
        df = pd.DataFrame(columns=["Publication Name", "DOI", "Abstract"])

        for i in data:
            if i["Abstract"]:
                rowDf = pd.DataFrame([[i["Title"], i["DOI"], i["Abstract"]]], columns=df.columns)
            else:
                rowDf = pd.DataFrame([[i["Title"], i["DOI"], ""]], columns=df.columns)
            df = df.append(rowDf)
        return df
