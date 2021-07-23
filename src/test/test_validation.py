import unittest
import numpy as np
from main.NLP.VALIDATION.validate_sdg_svm import ValidateSdgSvm

class ValidationTest(unittest.TestCase):

    def test_cosine_similarity_orthogonal(self):
        test_obj = ValidateSdgSvm()
        x1 = np.array([1.0, 0.0, 0.0])
        x2 = np.array([0.0, 0.0, 1.0])
        result = test_obj.compute_similarity(x1, x2)
        self.assertAlmostEqual(result, 0.0, msg="The vectors are orthogonal.")

    def test_cosine_similarity_parallel(self):
        test_obj = ValidateSdgSvm()
        x1 = np.array([1.0, 0.0, 0.0])
        x2 = np.array([1.0, 0.0, 0.0])
        result = test_obj.compute_similarity(x1, x2)
        self.assertAlmostEqual(result, 1.0, msg="The vectors are parallel.") 

    def test_cosine_similarity_range(self):
        result = True
        max_iter = 1000000
        for i in range(max_iter):
            test_obj = ValidateSdgSvm()
            X = np.random.dirichlet(np.ones(test_obj.num_sdgs), size=2) # generate random probability distribution
            x1 = X[0]
            x2 = X[1]
            in_range = 0.0 <= test_obj.compute_similarity(x1, x2) <= 1.0 # test output lies in the range [0,1]
            result = result and in_range
        self.assertTrue(result, "Cosine similarity output is in the range [0,1]")