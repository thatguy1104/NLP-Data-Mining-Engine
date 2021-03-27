import unittest
import socket
from src.main.SCOPUS.scrape import GetScopusData
class ScopusTest(unittest.TestCase):

    def test_invalid_scopus_api(self):
        test_obj = GetScopusData()
        result = test_obj.getInfo("non existent doi")
        test_obj.f.close()
        self.assertEqual(result, "invalid", "Error expected")

    def test_doi_retrieval(self):
        test_obj = GetScopusData()
        limit = 10
        result = test_obj.getDOIs(["DOI"], limit)
        test_obj.f.close()
        self.assertEqual(len(result), limit, "Expects dataframe of equal size")

        
