import unittest
import requests
from src.main.MODULE_CATALOGUE.INITIALISER.initialise_files import Initialiser
from src.main.MODULE_CATALOGUE.scrape import UCL_Module_Catalogue

class ModuleTest(unittest.TestCase):

    def test_ucl_api_request(self):
        test_obj = Initialiser()
        data = requests.get("https://uclapi.com/timetable/data/departments", params={"token": test_obj.token})
        self.assertEqual(data.status_code, 200, "Bad request to UCL API")

    def test_module_catalogue(self):
        test_obj = UCL_Module_Catalogue()
        modID = "CLNE0010"
        link = "https://www.ucl.ac.uk/module-catalogue/modules/neuromuscular-literature-review-CLNE0010"
        test_result = test_obj.get_module_data(link, modID)
        # print(test_result)
        self.assertEqual(len(test_result), 7, "Bad request to Module Catalogue")

    def test_failure_module_catalogue(self):
        test_obj = UCL_Module_Catalogue()
        modID = "some_invalid_module_id"
        link = "https://www.ucl.ac.uk/module-catalogue/modules/some_invalid_module_id"
        test_result = test_obj.get_module_data(link, modID)
        
        self.assertEqual(True, not all(test_result), "Bad request to Module Catalogue, supposed to fail")
