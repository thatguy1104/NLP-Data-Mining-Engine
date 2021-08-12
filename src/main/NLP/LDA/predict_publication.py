import os, sys
import json
import pickle
import pandas as pd
import gensim
import pymongo
from bson import json_util
from main.LOADERS.publication_loader import PublicationLoader
from main.CONFIG_READER.read import get_details

client = pymongo.MongoClient(get_details("MONGO_DB", "client"))
col = client.Scopus.PublicationPrediction

class ScopusPrediction():
    
    def __init__(self):
        self.publiction_data = pd.DataFrame(columns=['DOI', 'Title', 'Description'])
        self.model_name_SDG = "main/NLP/LDA/SDG_RESULTS/model.pkl"
        self.model_name_IHE = "main/NLP/LDA/IHE_RESULTS/model.pkl"
        self.loader = PublicationLoader()

    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __writeToDB_Scopus(self, data: dict) -> None:
        """
            Writes to MongoDB's PublicationPrediction cluster
        """
        col.update_one({"DOI": data["DOI"]}, {"$set": data}, upsert=True)

    def make_predictions_SDG(self, limit) -> None:
        """
            Uses LDA trained on modules to classify publications in accordance with SDG's
        """
        self.load_publications()

        results = {}
        papers = self.publiction_data.head(limit) if limit else self.publiction_data
        num_papers, counter = len(papers), 1

        with open(self.model_name_SDG, 'rb') as f:
            lda = pickle.load(f)
            for i in range(num_papers):
                self.__progress(counter, num_papers, "Predicting...")
                description = papers['Description'][i]

                X_predicted = lda.vectorizer.transform([description])
                C_predicted = gensim.matutils.Sparse2Corpus(X_predicted, documents_columns=False)
                topic_distribution = lda.model.get_document_topics(C_predicted)

                td = [x for x in topic_distribution]
                td = td[0]
                results[papers['DOI'][i]] = {}
                for topic, pr in td:
                    results[papers['DOI'][i]]['Title'] = papers['Title'][i]
                    results[papers['DOI'][i]]['DOI'] = papers['DOI'][i]
                    results[papers['DOI'][i]][str(topic + 1)] = str(pr)
                
                self.__writeToDB_Scopus(results[papers['DOI'][i]])
                counter += 1

        print()
        with open("main/NLP/LDA/SDG_RESULTS/scopus_prediction_results.json", "w") as f:
            json.dump(results, f)
        client.close()

    def __clean_training_results(self, data) -> dict:
        for key, val in data.items():
            contents = {}
            for i, elem in enumerate(val):
                temp_list = elem.replace("(", "").replace(")", "").replace("%", "").split(',')
                val[i] = (int(temp_list[0]), float(temp_list[1].replace(" ", "")))
                contents[str(val[i][0])] = val[i][1]
            data[key] = contents
        return data

    def __writeToDB_Scopus_IHE(self, data: dict) -> None:
        """
            Writes to MongoDB's IHEPRediction cluster
        """
        col_ihe_pred = client.Scopus.IHEPrediction

        c, l = 1, len(data)
        for i, val in data.items():
            self.__progress(c, l, "Pushing to Mongo IHE Predictions")
            col_ihe_pred.update_one({"DOI": i}, {"$set": val}, upsert=True)
        print()

    def make_predictions_IHE(self) -> None:
        """
            Uses LDA trained on 30,000 publications to classify the rest of the publications in accordance with IHE's
        """
        papers = self.loader.load_all()

        with open("main/NLP/LDA/IHE_RESULTS/training_results.json") as f:
            existing_papers = json.load(f)['Document Topics']
        existing_papers = self.__clean_training_results(existing_papers)

        resultser = {}
        num_papers, counter = len(papers), 1

        with open(self.model_name_IHE, 'rb') as f:
            lda = pickle.load(f)
            for i in papers:
                self.__progress(counter, num_papers, "Predicting IHE for unseen publications...")
                description = papers[i]['Description']


                X_predicted = lda.vectorizer.transform([description])
                C_predicted = gensim.matutils.Sparse2Corpus(X_predicted, documents_columns=False)
                topic_distribution = lda.model.get_document_topics(C_predicted)

                td = [x for x in topic_distribution]
                td = td[0]

                multiplier = 10 ** 1

                data = {}
                for index, topic in enumerate(td):
                    td[index] = (topic[0], int((topic[1] * 100) * multiplier) / multiplier)
                    data[str(td[index][0])] = td[index][1]

                existing_papers[i] = data
                counter += 1

        print()
        with open("main/NLP/LDA/IHE_RESULTS/scopus_prediction_results.json", "w") as f:
            json.dump(existing_papers, f)
        
        self.__writeToDB_Scopus_IHE(existing_papers)
        client.close()

    def load_publications(self) -> None:
        """
            Forms self.publiction_data (publication dataset)
        """

        data = self.loader.load_all()
        for i in data:
            i = json.loads(json_util.dumps(i))
            abstract = data[i]["Abstract"]
            doi = data[i]["DOI"]
            if abstract and doi:
                title = data[i]["Title"]
                author_keywords = data[i]['AuthorKeywords']
                index_keywords = data[i]['IndexKeywords']
                subject_areas = data[i]['SubjectAreas']

                concat_data_fields = title + " " + abstract
                if author_keywords:
                    concat_data_fields += " " + " ".join(author_keywords)
                if index_keywords:
                    concat_data_fields += " " + " ".join(index_keywords)
                if subject_areas:
                    subject_name = [x[0] for x in subject_areas]
                    concat_data_fields += " " + " ".join(subject_name)
                
                row_df = pd.DataFrame([[doi, title, concat_data_fields]], columns=self.publiction_data.columns)
                self.publiction_data = self.publiction_data.append(row_df, verify_integrity=True, ignore_index=True)

    def predict(self) -> None:
        """
            Controller function for this class
        """
        
        # self.make_predictions_SDG(limit=None)
        self.make_predictions_IHE()
