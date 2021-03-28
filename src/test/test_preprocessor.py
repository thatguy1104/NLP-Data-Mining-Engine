import unittest
import string
from src.main.NLP.PREPROCESSING.preprocessor import Preprocessor
from src.main.NLP.PREPROCESSING.module_preprocessor import ModuleCataloguePreprocessor

class PreprocessorTest(unittest.TestCase):

    def test_preprocessor_stopwords(self):
        test_obj = Preprocessor()
        stopword = "and"
        result = stopword in test_obj.stopwords
        self.assertTrue(result, "Found the word: '{}' in stopwords".format(stopword))

    def test_preprocessor_stopword_removal(self):
        test_obj = Preprocessor()
        text = "The sun is hot and the moon is cold" # text must contain stopwords for the test to pass.
        self.assertLess(len(test_obj.preprocess(text)), len(text), "len(preprocess(text)) < len(text)")

    def test_preprocessed_text_subset_of_text(self):
        text_obj = Preprocessor()
        text = "Climate change describes a change in the average conditions — such as temperature and rainfall."
        preprocessed_text = text_obj.preprocess(text)
        result = set(preprocessed_text).issubset(set(text))
        self.assertTrue(result, "preprocess(text) ⊆ text")

    def test_tokenize_remove_punctuation(self):
        text_obj = Preprocessor()
        text = "I enjoy programming, chess.. and tennis!!"
        tokenized_text = " ".join(text_obj.tokenize(text))
        result = [i for i in tokenized_text if i in string.punctuation]
        self.assertListEqual(result, [], "Tokenized text does not contain any punctuation")

    def test_tokenize_lowercase(self):
        text_obj = Preprocessor()
        text = "WHEN will we TEST - ModuleCataloguePreprocessor..."
        result = " ".join(text_obj.tokenize(text)).islower()
        self.assertTrue(result, "All characters in the tokenized text are lowercase")

    def test_module_preprocessor_stopwords(self):
        test_obj = ModuleCataloguePreprocessor()
        stopword = "module"
        result = stopword in test_obj.stopwords
        self.assertTrue(result, "Found the word: '{}' in stopwords".format(stopword))

    def test_tokenize_remove_module_code(self):
        text_obj = ModuleCataloguePreprocessor()
        module_code = "COMP0016"
        text = "The module {} is very fun!".format(module_code)
        result = module_code not in text_obj.tokenize(text)
        self.assertTrue(result, "Couldn't find the module code: '{}' in tokenized text".format(module_code))