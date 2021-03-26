import numpy as np
import pandas as pd
import logging
import pickle
import gensim
import nltk

from src.main.NLP.PREPROCESSING.preprocessor import Preprocessor
from src.main.LOADERS.loader import Loader
from src.main.MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

import pyLDAvis.gensim
import matplotlib.colors as mcolors
from sklearn.manifold import TSNE
from bokeh.plotting import figure, output_file, save
from bokeh.models import Label

class Lda():
    """
        The abstract class for implementing Latent Dirichlet Allocation (semi-supervised topic modelling algorithm).
        The eta priors can be alterned to guide topic convergence given an extensive set of keywords.
    """

    def __init__(self):
        """
            Initialize state of Lda with abstract preprocessor, data loader, data, list of topic keywords, number of topics,
            text vectorizer and model.
        """
        self.preprocessor = Preprocessor()
        self.loader = Loader()
        self.data = None # dataframe with columns {ID, Description}
        self.keywords = None # list of topic keywords.
        self.num_topics = 0
        self.vectorizer = self.get_vectorizer(1, 1, 1, 1)
        self.model = None

    def write_results(self, corpus, num_top_words: int, results_file: str):
        """
            Serializes the topic-word and document-topic distributions as a JSON file and pushes the data to MongoDB.
        """
        raise NotImplementedError

    def serialize(self, model_pkl_file: str):
        """
            Serializes the Lda object as a pickle file.
        """
        with open(model_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    def load_keywords(self, keywords: str):
        """
            Preprocess the list of topic keywords from the csv file path.
        """
        print("Loading keywords...")
        self.keywords = self.preprocessor.preprocess_keywords(keywords)

    def load_dataset(self, count: int):
        """
            Loads a fixed number of rows from the database as a dataframe object.
        """
        print("Loading dataset...")
        self.data = self.loader.load(count)
        print("Size before/after filtering -->",  str(count), "/", len(self.data))

    def get_vectorizer(self, min_n_gram: int, max_n_gram: int, min_df: float, max_df: float):
        """
            Returns text vectorizer with n-grams in the range [min_n_gram, max_n_gram] and the lower/upper document frequency threshold 
            for ignoring terms.
        """
        stopwords = [self.preprocessor.lemmatize(s) for s in self.preprocessor.stopwords] # lemmatize stopwords.
        return TfidfVectorizer(tokenizer=self.preprocessor.tokenize, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), 
                strip_accents='unicode', min_df=min_df, max_df=max_df)

    def lda_model(self, corpus, id2word: dict, eta, passes: int, iterations: int, chunksize: int):
        """
            Fits the LdaMulticore model for the given corpus, number of topics and vocabulary.
        """
        return gensim.models.LdaMulticore(corpus=corpus, num_topics=self.num_topics, id2word=id2word, random_state=42, chunksize=chunksize, eta=eta,
                eval_every=None, passes=passes, iterations=iterations, workers=3, alpha="symmetric", minimum_probability=0, per_word_topics=True)

    def topic_seeds(self):
        """
            Returns the topic seeds as a dictionary with the keyword as keys and a list of topic numbers as values.
        """
        feature_names = self.vectorizer.get_feature_names() # list of n-grams of words.
        seed_topics = {} # dictionary of keyword to topic_id.
        for topic_id, topic_keywords in enumerate(self.keywords):
            for keyword in topic_keywords:
                if keyword in feature_names:
                    seed_topics.setdefault(keyword, []).append(topic_id) # one-to-many mapping from keyword to topic_id.
        print(seed_topics, "\n")
        return seed_topics

    def create_eta(self, priors: dict, eta_dictionary: dict):
        """
            Sets the eta hyperparameter as a symmetric prior distribution over word weights in each topic.
        """
        num_terms = len(eta_dictionary)
        return np.full(shape=(self.num_topics, num_terms), fill_value=1) # topic-term matrix filled with the value 1.

    def train(self, passes: int, iterations: int, chunksize: int):
        """
            Trains the LDA model by calling fit_transform on the description text, creating the corpus, topic seeds, eta and fitting 
            the model.
        """
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        X = self.vectorizer.fit_transform(self.data.Description) # map description to a document-count matrix.
        corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False) # transform sparse matrix as a gensim corpus. 
        id2word = dict((v, k) for k, v in self.vectorizer.vocabulary_.items())

        topic_seeds = self.topic_seeds()
        eta = self.create_eta(topic_seeds, id2word)
        with (np.errstate(divide='ignore')):
            self.model = self.lda_model(corpus, id2word, eta, passes, iterations, chunksize)
            
        return corpus

    def display_perplexity(self, corpus):
        """
            Prints the perplexity score predicted by the model.
        """
        print('Perplexity: {:.2f}'.format(self.model.log_perplexity(corpus)))   

    def display_topic_words(self, num_top_words: int):
        """
            Prints the topic-word distribution with num_top_words words for each topic.
        """
        raise NotImplementedError
    
    def display_document_topics(self, corpus):
        """
            Prints the document-topic distribution for each document in the corpus.
        """
        raise NotImplementedError

    def pyldavis(self, corpus, output_file: str):
        """
            Runs the pyLDAvis package which help interpet the topics in a topic model that has been fit to the corpus of text data. 
            The visualization is saved to a stand-alone HTML file.
        """
        dictionary = gensim.corpora.Dictionary()
        word2id = dict((k, v) for k, v in self.vectorizer.vocabulary_.items())
        dictionary.id2token = self.model.id2word
        dictionary.token2id = word2id
        visualization = pyLDAvis.gensim.prepare(self.model, corpus, dictionary=dictionary, sort_topics=False)
        pyLDAvis.save_html(visualization, output_file)

    def t_sne_cluster(self, corpus, output_file: str):
        """
            Runs the t-distributed Stochastic Neighbor Embedding (t-SNE) tool to visualize high-dimensional data.
            Uses the PCA (Principal Component Analysis) dimensionality reduction method.
        """
        # Compute weights for each topic.
        topic_weights = []
        for i, row_list in enumerate(self.model[corpus]):
            topic_weights.append([w for i, w in row_list[0]])
        
        df = pd.DataFrame(topic_weights).fillna(0).values # topic weights dataframe.
        df = df[np.amax(df, axis=1) > 0.35]

        topic = np.argmax(df, axis=1) # highest related topic.

        # Apply t-SNE dimensionality reduction.
        tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca') # reduces dimension of embedded space to 2.
        tsne_lda = tsne_model.fit_transform(df)

        # Plot topic clusters.
        colors = np.array([color for name, color in mcolors.CSS4_COLORS.items()])
        plot = figure(title="t-SNE Clustering of {} Topics".format(self.num_topics),  plot_width=2000, plot_height=1500)
        plot.scatter(x=tsne_lda[:,0], y=tsne_lda[:,1], color=colors[topic])
        
        save(plot, filename=output_file)

    def display_results(self, corpus, num_top_words: int, pyldavis_html: str, t_sne_cluster_html: str):
        """
            Display perplexity, topic-word distribution, document-topic distribution, Lda visualization and t-SNE clustering.
        """
        self.display_perplexity(corpus)
        self.display_topic_words(num_top_words) # topic-word distribution.
        self.display_document_topics(corpus) # document-topic distribution.

        self.pyldavis(corpus, pyldavis_html)
        self.t_sne_cluster(corpus, t_sne_cluster_html)

    def run(self):
        """
            Initializes Lda parameters, trains the model and saves the results.
        """
        raise NotImplementedError
