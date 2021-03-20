import pymongo
import json
import ssl
import os
import pandas as pd
import pickle

from LOADERS.loader import Loader
from bson import json_util

class PublicationLoader(Loader):
    def __init__(self):
        self.host = "mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        self.data_file = "LOADERS/publications.pkl"
        self.prediction_path = "NLP/LDA/SDG_RESULTS/prediction_results.json"
        self.string_matches_path = "NLP/STRING_MATCH/SDG_RESULTS/scopus_matches.json"

    def combine_text_fields(self, publication: dict) -> str:
        """
            Concatinate all publication data that is descriptive of it.
            Fields include: title, abstract, author keywords, index keywords (assigned by Scopus)
        """
        title = publication["Title"] if publication["Title"] else ""
        abstract = publication["Abstract"] if publication["Abstract"] else ""
        author_keywords = " ".join(publication["AuthorKeywords"]) if publication["AuthorKeywords"] else ""
        index_keywords = " ".join(publication["IndexKeywords"]) if publication["IndexKeywords"] else "" 
        description = [title, abstract, author_keywords, index_keywords]
        return " ".join(description)

    def load_all(self) -> dict:
        """
            Load publication data from serialised file.
            Restructures data into dictionary data structure.
        """
        with open(self.data_file, "rb") as input_file:
            data = pickle.load(input_file)
            
        resulting_data = {}
        for publication in data:
            publication["Description"] = self.combine_text_fields(publication)
            publication.pop("_id", None)
            resulting_data[publication["DOI"]] = publication

        return resulting_data

    def load(self, count: int):
        """
            Loads publication data with an option of limiting number of data points returned.
            Returns Pandas DataFrame with columns: 'DOI', 'Title', 'Description'
        """
        with open(self.data_file, "rb") as input_file:
            data = pickle.load(input_file)
        data = dict(list(data.items())[:count]) if isinstance(count, int) else data
        
        df = pd.DataFrame(columns=["DOI", "Title", "Description"])
        for publication in data:
            title = publication["Title"]
            doi = publication["DOI"]
            description = self.combine_text_fields(publication)
            row_df = pd.DataFrame([[doi, title, description]], columns=df.columns)
            df = df.append(row_df)
    
        return df

    def load_prediction_results(self):
        """
            Loads publication SDG predictions from a serialised file, if it exists, otherwise from MongoDB
        """
        if os.path.exists(self.prediction_path):
            with open(self.prediction_path) as json_file:
                data = json.load(json_file)
        else:
            client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
            db = client.Scopus
            col = db.PublicationPrediction
            data = col.find(batch_size=10)
            client.close()

            
            
        return data

    def load_string_matches_results(self):
        """
            Loads publication SDG keyword string match results from serialised file, if it exists, otherwise from MongoDB
        """
        if os.path.exists(self.string_matches_path):
            with open(self.string_matches_path) as json_file:
                data = json.load(json_file)
        else:
            client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
            db = client.Scopus
            col = db.MatchedScopus
            data = col.find(batch_size=10)
            client.close()

        return data

    def load_pymongo_db(self):
        """
            Download publication data from MongoDB and serialises it to <publications.pkl>
        """
        print("Loading publications from pymongo database...")
        client = pymongo.MongoClient(self.host, ssl_cert_reqs=ssl.CERT_NONE)
        db = client.Scopus
        col = db.Data
        data = col.find(batch_size=10)
        client.close()

        result = []
        for publication in data:
            publication = json.loads(json_util.dumps(publication))
            del publication['_id']
            result.append(publication)

        with open(self.data_file, "wb") as output_file:
            pickle.dump(result, output_file)
