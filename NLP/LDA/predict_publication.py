import os, sys
import json
import pickle
import pandas as pd
import gensim

class ScopusMap():
    def __init__(self):
        self.publication_files_directory = "SCOPUS/GENERATED_FILES/"
        self.publiction_data = pd.DataFrame(columns=['DOI', 'Title', 'Description'])
        self.model_name = "NLP/LDA/lda_model.pkl"

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def make_predictions(self, limit):
        results = {}
        counter = 1
        papers = self.publiction_data.head(limit) if limit else self.publiction_data
        num_papers = len(papers)

        with open(self.model_name, 'rb') as f:
            lda = pickle.load(f)
            for i in range(num_papers):
                self.progress(counter, num_papers, "Predicting...")
                description = papers['Description'][i]

                X_predicted = lda.vectorizer.transform([description])
                C_predicted = gensim.matutils.Sparse2Corpus(X_predicted, documents_columns=False)
                topic_distribution = lda.model.get_document_topics(C_predicted)

                td = [x for x in topic_distribution]
                td = td[0]
                results[papers['DOI'][i]] = {}
                for topic, pr in td:
                    results[papers['DOI'][i]]['Title'] = papers['Title'][i]
                    results[papers['DOI'][i]][topic + 1] = str(pr)
                counter += 1

        print()
        with open("NLP/MODEL_RESULTS/scopus_prediction_results.json", "w") as f:
            json.dump(results, f)

    def load_publication(self, file_name):
        with open(self.publication_files_directory + file_name) as json_file:
            data = json.load(json_file)
            if not data:
                return

            abstract = data["Abstract"]
            doi = data["DOI"]
            if abstract and doi:
                title = data["Title"]
                author_keywords = data['AuthorKeywords']
                index_keywords = data['IndexKeywords']
                subject_areas = data['SubjectAreas']

                concat_data_fields = title + " " + abstract
                if author_keywords:
                    concat_data_fields += " " + " ".join(author_keywords)
                if index_keywords:
                    concat_data_fields += " " + " ".join(index_keywords)
                if subject_areas:
                    subject_name = [x[0] for x in subject_areas]
                    concat_data_fields += " " + " ".join(subject_name)
                
                return pd.DataFrame([[doi, title, concat_data_fields]], columns=self.publiction_data.columns)

    def load_publications(self):
        file_names = os.listdir(self.publication_files_directory)
        for file_name in file_names:
            row_df = self.load_publication(file_name)
            self.publiction_data = self.publiction_data.append(row_df, verify_integrity=True, ignore_index=True)

    def predict(self):
        self.load_publications()
        self.make_predictions(limit=None)