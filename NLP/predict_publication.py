import os, sys
import json
import pickle
import pandas as pd
import gensim


class PredictFromLDA():
    def __init__(self):
        self.publication_files_directory = "../SCOPUS/GENERATED_FILES/"
        self.publicationData = pd.DataFrame(columns=['DOI', 'Title', 'Description'])
        self.modelName = "lda_model.pkl"

    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def makePrediction(self, limit):
        results = {}
        counter = 1

        if limit:
            papers = self.publicationData.head(limit)
        else:
            papers = self.publicationData
        l = len(papers)

        with open(self.modelName, 'rb') as f:
            lda = pickle.load(f)

            for i in range(l):
                self.progress(counter, l, "Predicting...")
                description = papers['Description'][i]    

                X_predicted = lda.vectorizer.transform([description])
                C_predicted = gensim.matutils.Sparse2Corpus(X_predicted, documents_columns=False)
                topic_distribution = lda.model.get_document_topics(C_predicted)

                td = [x for x in topic_distribution]
                td = td[0]
                td.sort(key=lambda x: x[1], reverse=True)

                results[papers['DOI'][i]] = {}
                for topic, pr in td:
                    results[papers['DOI'][i]]['Title'] = papers['Title'][i]
                    results[papers['DOI'][i]][topic + 1] = str(pr)
                counter += 1
        print()
        with open("ModelResults/sdgAssignments.json", "w") as f:
            json.dump(results, f)

    def makePredictionDOI(self):
        assert len(self.publicationData == 1), "Invalid EID provided"
        paper = self.publicationData
        description = paper['Description'][0]

        with open(self.modelName, 'rb') as f:
            lda = pickle.load(f)

            X_predicted = lda.vectorizer.transform([description])
            C_predicted = gensim.matutils.Sparse2Corpus(X_predicted, documents_columns=False)
            topic_distribution = lda.model.get_document_topics(C_predicted)

            td = [x for x in topic_distribution]
            td = td[0]
            td.sort(key=lambda x: x[1], reverse=True)

            print('DOI: {}\n\nDescription: {}\n'.format(paper['DOI'][0], description))
            for topic, pr in td:
                print('SDG {}: {}'.format(topic + 1, pr))

    def loadAllData(self):
        fileNames = os.listdir(self.publication_files_directory)
        for i in fileNames:
            with open(self.publication_files_directory + i, 'rb') as json_file:
                data_ = json.load(json_file)
                if data_:
                    doi = data_['DOI']
                    title = data_['Title']
                    concatDataFields = data_['Title']
                    if data_['Abstract']:
                        concatDataFields += data_['Abstract']
                    if data_['AuthorKeywords']:
                        concatDataFields += " ".join(data_['AuthorKeywords'])
                    if data_['IndexKeywords']:
                        concatDataFields += " ".join(data_['IndexKeywords'])
                    if data_['SubjectAreas']:
                        subjectName = [x[0] for x in data_['SubjectAreas']]
                        concatDataFields += " ".join(subjectName)
                    rowDataFrame = pd.DataFrame([[doi, title, concatDataFields]], columns=self.publicationData.columns)
                    self.publicationData = self.publicationData.append(rowDataFrame, verify_integrity=True, ignore_index=True)

    def loadPaper(self, EID):
        fileName = self.publication_files_directory + EID + '.json'
        with open(fileName, 'rb') as json_file:
            data_ = json.load(json_file)
            if data_:
                doi = data_['DOI']
                title = data_['Title']
                concatDataFields = data_['Title']
                if data_['Abstract']:
                    concatDataFields += data_['Abstract']
                if data_['AuthorKeywords']:
                    concatDataFields += " ".join(data_['AuthorKeywords'])
                if data_['IndexKeywords']:
                    concatDataFields += " ".join(data_['IndexKeywords'])
                if data_['SubjectAreas']:
                    subjectName = [x[0] for x in data_['SubjectAreas']]
                    concatDataFields += " ".join(subjectName)
                rowDataFrame = pd.DataFrame([[doi, title, concatDataFields]], columns=self.publicationData.columns)
                self.publicationData = self.publicationData.append(rowDataFrame, verify_integrity=True, ignore_index=True)

    def run(self):
        """ FOR SINGLE PAPER CLASSIFICATION """
        # EID = '2-s2.0-85019224026' # climate change
        # EID = '2-s2.0-84961616003' # programming
        # EID = '2-s2.0-84948716653' # gender equality
        # EID = '2-s2.0-0000717472'
        # self.loadPaper(EID)
        # self.makePredictionDOI()

        """ FOR COLLECTIVE CLASSIFICATION """
        self.loadAllData()
        self.makePrediction(limit=None)


obj = PredictFromLDA()
obj.run()
