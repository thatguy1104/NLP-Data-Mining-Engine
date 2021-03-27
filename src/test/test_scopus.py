import unittest
import socket
from src.main.SCOPUS.scrape import GetScopusData
class ScopusTest(unittest.TestCase):

    def test_invalid_scopus_api(self):
        test_obj = GetScopusData()
        result = test_obj.getInfo("non existent doi")
        self.assertEqual(result, "invalid", "Error expected")
