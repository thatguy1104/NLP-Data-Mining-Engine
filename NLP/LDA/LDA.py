import numpy as np
import pandas as pd
import logging
import pickle
import gensim
import nltk

from NLP.PREPROCESSING.preprocessor import Preprocessor
from LOADERS.loader import Loader

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import pyLDAvis.gensim
import matplotlib.colors as mcolors
from sklearn.manifold import TSNE
from bokeh.plotting import figure, output_file, save
from bokeh.models import Label

class Lda():
    def __init__(self):
        self.loader = Loader()
        self.preprocessor = Preprocessor()
        self.data = None # dataframe with columns {ID, Description}
        self.keywords = None # list of topic keywords
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 1, 1, 1)
        self.model = None

    def load_keywords(self, keywords):
        print("Loading keywords...")
        self.keywords = self.preprocessor.preprocess_keywords(keywords)

    def load_dataset(self, count):
        print("Loading dataset...")
        self.data = self.loader.load(count)
        print("Size before/after filtering -->",  str(count), "/", len(self.data))

    def get_vectorizer(self, min_n_gram, max_n_gram, min_df, max_df):
        stopwords = [self.preprocessor.lemmatize(s) for s in self.preprocessor.stopwords] # lemmatize stopwords.
        return TfidfVectorizer(tokenizer=self.preprocessor.tokenize, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), 
                strip_accents='unicode', min_df=min_df, max_df=max_df)

    def lda_model(self, corpus, id2word, eta, passes, iterations):
        return gensim.models.LdaMulticore(corpus=corpus, num_topics=self.num_topics, id2word=id2word, random_state=42, chunksize=5000, eta=eta,
                eval_every=None, passes=passes, iterations=iterations, workers=3, alpha="symmetric", minimum_probability=0, per_word_topics=True)

    def topic_seeds(self):
        feature_names = self.vectorizer.get_feature_names() # list of n-grams of words.
        seed_topics = {} # dictionary of keyword to topic_id.
        for topic_id, topic_keywords in enumerate(self.keywords):
            for keyword in topic_keywords:
                if keyword in feature_names:
                    seed_topics.setdefault(keyword, []).append(topic_id) # one-to-many mapping from keyword to topic_id.
        print(seed_topics, "\n")
        return seed_topics

    def create_eta(self, priors, eta_dictionary):
        num_terms = len(eta_dictionary)
        return np.full(shape=(self.num_topics, num_terms), fill_value=1) # topic-term matrix filled with the value 1.

    def train(self, passes, iterations):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        X = self.vectorizer.fit_transform(self.data.Description) # map description to a document-count matrix.
        corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)
        id2word = dict((v, k) for k, v in self.vectorizer.vocabulary_.items())

        topic_seeds = self.topic_seeds()
        eta = self.create_eta(topic_seeds, id2word)
        with (np.errstate(divide='ignore')):
            self.model = self.lda_model(corpus, id2word, eta, passes, iterations)
            
        return corpus

    def display_perplexity(self, corpus):
        print('Perplexity: {:.2f}'.format(self.model.log_perplexity(corpus)))   

    def display_topic_words(self, num_top_words):
        for n in range(self.num_topics):
            print('SDG {}: {}'.format(n + 1, [self.model.id2word[w] for w, p in self.model.get_topic_terms(n, topn=num_top_words)]))
    
    def display_document_topics(self, corpus):
        documents = self.data.Module_ID
        count = 0
        for d, c in zip(documents, corpus):
            if count % 25 == 0:
                doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
                print('{} {}'.format(d, doc_topics))
            count += 1

    def pyldavis(self, corpus, output_file):
        dictionary = gensim.corpora.Dictionary()
        word2id = dict((k, v) for k, v in self.vectorizer.vocabulary_.items())
        dictionary.id2token = self.model.id2word
        dictionary.token2id = word2id
        visualization = pyLDAvis.gensim.prepare(self.model, corpus, dictionary=dictionary, sort_topics=False)
        pyLDAvis.save_html(visualization, output_file)

    def t_sne_cluster(self, corpus, output_file):
        # Find topic weights.
        topic_weights = []
        for i, row_list in enumerate(self.model[corpus]):
            topic_weights.append([w for i, w in row_list[0]])

        df = pd.DataFrame(topic_weights).fillna(0).values # topic weights dataframe.
        df = df[np.amax(df, axis=1) > 0.35]

        topic = np.argmax(df, axis=1) # highest related topic.

        # t-SNE dimensionality reduction.
        tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca')
        tsne_lda = tsne_model.fit_transform(df)

        # Plot topic clusters.
        colors = np.array([color for name, color in mcolors.CSS4_COLORS.items()])
        plot = figure(title="t-SNE Clustering of {} Topics".format(self.num_topics),  plot_width=2000, plot_height=1500)

        plot.scatter(x=tsne_lda[:,0], y=tsne_lda[:,1], color=colors[topic])
        save(plot, filename=output_file)

    def display_results(self, corpus, num_top_words, pyldavis_html, t_sne_cluster_html):
        self.display_perplexity(corpus) # perplexity.
        self.display_topic_words(num_top_words) # topic-word distribution.
        self.display_document_topics(corpus) # document-topic distribution.

        # self.pyldavis(corpus, pyldavis_html) # pyLDAvis distance map.
        self.t_sne_cluster(corpus, t_sne_cluster_html) # t-SNE clustering.
    
    def push_to_mongo(self, data):
        raise NotImplementedError

    def write_results(self, corpus, num_top_words, results_file):
        raise NotImplementedError

    def serialize(self, model_pkl_file):
        with open(model_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    def run(self):
        raise NotImplementedError
