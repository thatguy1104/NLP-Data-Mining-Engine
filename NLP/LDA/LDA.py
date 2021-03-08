import gensim
import numpy as np
import pandas as pd
import nltk
import json
import logging
import pyLDAvis
import pyLDAvis.gensim

from gensim import corpora
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from NLP.preprocess import module_catalogue_tokenizer, text_lemmatizer, get_stopwords

import matplotlib.colors as mcolors
from sklearn.manifold import TSNE
from bokeh.plotting import figure, output_file, save
from bokeh.models import Label

class LDA():
    def __init__(self, data, keywords):
        self.data = data # module-catalogue data frame with columns {ModuleID, Description}.
        self.keywords = keywords # list of topic keywords.
        self.vectorizer = self.create_vectorizer(1, 3, 1, 0.03)
        self.n_topics = len(self.keywords)

    def create_vectorizer(self, min_n_gram, max_n_gram, min_df, max_df):
        stopwords = [text_lemmatizer(s) for s in get_stopwords()] # lemmatize stopwords.
        return TfidfVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), strip_accents='unicode', 
                min_df=min_df, max_df=max_df)

    # optimized alpha [0.07905018, 0.021635817, 0.02065896, 0.021123013, 0.022771074, 0.26609096, 0.017549414, 0.02452033, 0.02282285, 0.03086126, 0.023378693, 0.02263801, 0.021001419, 0.017342038, 0.023954913, 0.024656, 0.019133672, 0.024959238]

    def create_model(self, corpus, id2word, eta, n_passes, n_iterations):
        return gensim.models.LdaMulticore(corpus=corpus, num_topics=self.n_topics, id2word=id2word, random_state=42, chunksize=5000, eta=eta,
                eval_every=None, passes=n_passes, iterations=n_iterations, workers=3, alpha="symmetric", minimum_probability=0, per_word_topics=True)

    def create_topic_seeds(self):
        tf_feature_names = self.vectorizer.get_feature_names() # list of words or ngrams of words.
        seed_topics = {} # dictionary of keyword to topic_id.
        for t_id, keywords in enumerate(self.keywords):
            for keyword in keywords:
                if keyword in tf_feature_names:
                    seed_topics.setdefault(keyword, []).append(t_id) # one-to-many mapping from keyword to topic.
        print(seed_topics, "\n")
        return seed_topics

    def create_eta(self, priors, eta_dictionary):
        eta = np.full(shape=(self.n_topics, len(eta_dictionary)), fill_value=1) # (n_topics, n_terms) matrix filled with 1s.
        for keyword, topics in priors.items():
            keyindex = [index for index, term in eta_dictionary.items() if term == keyword]

            if len(keyindex) > 0:
                for topic in topics:
                    eta[topic, keyindex[0]] = 1e6

        #eta = np.divide(eta, eta.sum(axis=0))
        return eta

    def train(self, n_passes, n_iterations, num_top_words):
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        X = self.vectorizer.fit_transform(self.data.Description) # map description column to a matrix with documents as rows and counts as columns.
        corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)
        id2word = dict((v, k) for k, v in self.vectorizer.vocabulary_.items())

        seed_topics = self.create_topic_seeds()
        eta = self.create_eta(seed_topics, id2word)

        with (np.errstate(divide='ignore')):
            self.model = self.create_model(corpus, id2word, eta, n_passes, n_iterations)
        
        # Display perplexity, topic-word distribution and document-topic distribution.
        self.display_perplexity(corpus)
        print()
        self.display_topic_words(num_top_words)
        print()
        self.display_document_topics(corpus)

        self.writeResults(corpus, num_top_words) # record current results.

        # Visualize model using pyLDAvis.
        # self.visualize_model(corpus)

    def display_perplexity(self, corpus):
        print('Perplexity: {:.2f}'.format(self.model.log_perplexity(corpus)))   

    def display_topic_words(self, num_top_words):
        for n in range(self.n_topics):
            print('SDG {}: {}'.format(n + 1, [self.model.id2word[w] for w, p in self.model.get_topic_terms(n, topn=num_top_words)]))
    
    def display_document_topics(self, corpus):
        documents = self.data.Module_ID
        count = 0
        for d, c in zip(documents, corpus):
            if count % 25 == 0:
                doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
                print('{} {}'.format(d, doc_topics))
            count = count + 1

    def py_lda_vis(self, corpus):
        d = corpora.Dictionary()
        word2id = dict((k, v) for k, v in self.vectorizer.vocabulary_.items())
        d.id2token = self.model.id2word
        d.token2id = word2id
        visualization = pyLDAvis.gensim.prepare(self.model, corpus, dictionary=d, sort_topics=False)
        pyLDAvis.save_html(visualization, 'LDA.html')

    def writeResults(self, corpus, num_top_words):
        data = {}
        data['Perplexity'] = self.model.log_perplexity(corpus)
        data['Topic Words'] = {}
        for n in range(self.n_topics):
            data['Topic Words'][n + 1] = [self.model.id2word[w]for w, p in self.model.get_topic_terms(n, topn=num_top_words)]

        data['Document Topics'] = {}
        documents = self.data.Module_ID
        for d, c in zip(documents, corpus):
            doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
            data['Document Topics'][d] = doc_topics

        with open('NLP/MODEL_RESULTS/training_results.json', 'w') as outfile:
            json.dump(data, outfile)

    def tSNE_cluster(self, corpus):
        # Find topic weights.
        topic_weights = []
        for i, row_list in enumerate(self.model[corpus]):
            topic_weights.append([w for i, w in row_list[0]])

        df = pd.DataFrame(topic_weights).fillna(0).values # topic weights dataframe.
        df = df[np.amax(df, axis=1) > 0.35]

        topic = np.argmax(df, axis=1) # highest related topic (SDG).

        # t-SNE Dimensionality Reduction.
        tsne_model = TSNE(n_components=2, verbose=1, random_state=0, angle=.99, init='pca')
        tsne_lda = tsne_model.fit_transform(df)

        # Plot topic clusters.
        colors = np.array([color for name, color in mcolors.TABLEAU_COLORS.items()])
        plot = figure(title="t-SNE Clustering of {} SDGs".format(self.n_topics),  plot_width=2000, plot_height=1500)

        plot.scatter(x=tsne_lda[:,0], y=tsne_lda[:,1], color=colors[topic])
        output_file("t_sne_clusters.html")
        save(plot)
