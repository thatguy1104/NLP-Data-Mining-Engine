import gensim
import numpy as np
import nltk
import logging
import pyLDAvis
import pyLDAvis.gensim

from gensim import corpora
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from preprocess import module_catalogue_tokenizer, text_lemmatizer, get_stopwords
from ModelResults.resultsProcessing import ProcessResults

class LDA():
    def __init__(self, data, keywords):
        self.data = data # module-catalogue data frame with columns {ModuleID, Description}.
        self.keywords = keywords # topic keywords list.
        self.vectorizer = self.create_vectorizer(1, 3, 1, 0.03)
        #self.vectorizer = self.create_vectorizer(1, 1, 1, 1)
        self.n_topics = len(self.keywords)

    def create_vectorizer(self, min_n_gram, max_n_gram, min_df, max_df):
        stopwords = [text_lemmatizer(s) for s in get_stopwords()] # lemmatize stopwords.
        return TfidfVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram),
            strip_accents='unicode', min_df=min_df, max_df=max_df)
        #return CountVectorizer(tokenizer=module_catalogue_tokenizer, stop_words=stopwords, ngram_range=(min_n_gram, max_n_gram), 
            #strip_accents='unicode', min_df=min_df, max_df=max_df)

    # 1e4
    # optimized alpha [0.07905018, 0.021635817, 0.02065896, 0.021123013, 0.022771074, 0.26609096, 0.017549414, 0.02452033, 0.02282285, 0.03086126, 0.023378693, 0.02263801, 0.021001419, 0.017342038, 0.023954913, 0.024656, 0.019133672, 0.024959238]

    def create_model(self, corpus, id2word, eta, n_passes, n_iterations):
        #return gensim.models.LdaModel(corpus=corpus, num_topics=self.n_topics, id2word=id2word, random_state=42, chunksize=5000, eta=eta,
            #update_every=1, passes=n_passes, alpha='auto', minimum_probability=0, per_word_topics=True)
        return gensim.models.LdaMulticore(corpus=corpus, num_topics=self.n_topics, id2word=id2word, random_state=42, chunksize=5000, eta=eta, 
            eval_every=None, passes = n_passes, iterations=n_iterations, workers=5, alpha='symmetric', minimum_probability=0, per_word_topics=True)

    def create_topic_seeds(self):
        tf_feature_names = self.vectorizer.get_feature_names() # list of words or ngrams of words.
        seed_topics = {} # dictionary of keyword to topic_id.
        for t_id, keywords in enumerate(self.keywords):
            for keyword in keywords:
                if keyword in tf_feature_names:
                    seed_topics.setdefault(keyword, []).append(t_id) # one-to-many mapping from keyword to topic.
                    #seed_topics[keyword] = t_id
        print(seed_topics)
        print()
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

        X = self.vectorizer.fit_transform(self.data.Description) # maps description column to matrix of documents (rows) and counts (columns).
        corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)
        id2word = dict((v, k) for k, v in self.vectorizer.vocabulary_.items())

        seed_topics = self.create_topic_seeds()
        eta = self.create_eta(seed_topics, id2word)

        with (np.errstate(divide='ignore')):
            self.model = self.create_model(corpus, id2word, eta, n_passes, n_iterations)
        
        # Display perplexity, topic-word and document-topic distributions.
        self.display_perplexity(corpus)
        print()
        self.display_topic_words(num_top_words)
        print()
        self.display_document_topics(corpus)

        # Visualize model using pyLDAvis.
        self.visualize_model(corpus)

    def display_perplexity(self, corpus):
        print('Perplexity: {:.2f}'.format(self.model.log_perplexity(corpus)))   

    def display_topic_words(self, num_top_words):
        for n in range(self.n_topics):
            print('SDG {}: {}'.format(n + 1, [self.model.id2word[w] for w, p in self.model.get_topic_terms(n, topn=num_top_words)]))

    def display_document_topics(self, corpus):
        documents = self.data.Module_ID #self.data.Description
        count = 0
        for d, c in zip(documents, corpus):
            if count % 25 == 0:
                doc_topics = ['({}, {:.1%})'.format(topic + 1, pr) for topic, pr in self.model.get_document_topics(c)]
                print('{} {}'.format(d, doc_topics))
            count = count + 1

    def visualize_model(self, corpus):
        d = corpora.Dictionary()
        word2id = dict((k, v) for k, v in self.vectorizer.vocabulary_.items())
        d.id2token = self.model.id2word
        d.token2id = word2id
        visualization = pyLDAvis.gensim.prepare(self.model, corpus, dictionary=d, sort_topics=False)
        pyLDAvis.save_html(visualization, 'GuidedLDA_Visualization.html')
