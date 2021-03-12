import time, datetime
import json
import pymongo

from NLP.LDA.lda import Lda
from NLP.PREPROCESSING.module_preprocessor import ModuleCataloguePreprocessor
from LOADERS.module_loader import ModuleLoader

class SdgLda(Lda):
    def __init__(self):
        self.preprocessor = ModuleCataloguePreprocessor()
        self.loader = ModuleLoader()
        self.data = None # module-catalogue dataframe with columns {ModuleID, Description}.
        self.keywords = None # list of SDG-specific keywords.
        self.num_topics = len(self.keywords)
        self.vectorizer = self.get_vectorizer(1, 3, 1, 0.03)
        self.model = None

    def push_to_mongo(self, data):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.ModulePrediction
        key = value = data
        col.update_one(key, {"$set": value}, upsert=True)
        client.close()

    def write_results(self, corpus, num_top_words, results_file):
        data = {}
        data['Perplexity'] = self.model.log_perplexity(corpus)

        data['Topic Words'] = {}
        for n in range(self.num_topics):
            data['Topic Words'][str(n + 1)] = [self.model.id2word[w]for w, p in self.model.get_topic_terms(n, topn=num_top_words)]

        data['Document Topics'] = {}
        documents = self.data.Module_ID
        for d, c in zip(documents, corpus):
            doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
            data['Document Topics'][str(d)] = doc_topics

        self.push_to_mongo(data)
        with open(results_file, 'w') as outfile:
            json.dump(data, outfile)

    def run(self):
        ts = time.time()
        startTime = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        num_modules = "MAX"
        keywords = "MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv"
        passes = 10
        iterations = 400
        num_top_words = 20

        pyldavis_html = "NLP/LDA/SDG_RESULTS/pyldavis.html"
        tsne_clusters_html = "NLP/LDA/SDG_RESULTS/tsne_clusters.html"
        model = "NLP/LDA/SDG_RESULTS/model.pkl"
        results = "NLP/LDA/SDG_RESULTS/training_results.json"

        self.load_dataset(num_modules)
        self.load_keywords(keywords)
        
        print("Training...")
        corpus = self.train(passes, iterations)
        self.display_results(corpus, num_top_words, pyldavis_html, tsne_clusters_html)

        print("Saving results...")
        self.write_results(corpus, num_top_words, results) # record current results.
        self.serialize(model)