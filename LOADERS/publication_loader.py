import pymongo
import json
import pandas as pd

from LOADERS.loader import Loader
from bson import json_util

class PublicationLoader(Loader):
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.db = self.client.Scopus
        self.col = self.db.Data

    def combine_text_fields(self, publication):
        title = publication["Title"] if publication["Title"] else ""
        abstract = publication["Abstract"] if publication["Abstract"] else ""
        author_keywords = " ".join(publication["AuthorKeywords"]) if publication["AuthorKeywords"] else ""
        index_keywords = " ".join(publication["IndexKeywords"]) if publication["IndexKeywords"] else "" 
        description = [title, abstract, author_keywords, index_keywords]
        return " ".join(description)

    def load(self):
        resulting_data = {}
        data = self.col.find()

        for publication in data:
            publication = json.loads(json_util.dumps(publication))
            publication["Description"] = self.combine_text_fields(publication)
            publication.pop("_id", None)
            resulting_data[publication["DOI"]] = publication

        return resulting_data

    def load(self, count):            
        data = self.col.find().limit(count) if isinstance(count, int) else self.col.find()
        df = pd.DataFrame(columns=["Title", "DOI", "Description"])

        for publication in data:
            #publication = json.loads(json_util.dumps(publication))
            title = publication["Title"]
            doi = publication["DOI"]
            description = self.combine_text_fields(publication)
            row_df = pd.DataFrame([[title, doi, description]], columns=df.columns)
            df = df.append(row_df)
    
        return pd.DataFrame(data=df, columns=["DOI", "Description"])
