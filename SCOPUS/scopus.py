import requests
import json
import os
import textwrap
import pandas as pd


class Scopus():
    def __init__(self):
        self.scopus_2k_sample = "scopus_first_2k_sample.csv"
        self.rps_data_file = "cleaned_RPS_export_2015.csv"
        self.scopus_api_key = "325461529e8434763946ce3efc38b9f1"

    def getDOIs(self, columns, limit=None):
        if not limit:
            return pd.read_csv(self.rps_data_file)[columns]
        return pd.read_csv(self.rps_data_file)[columns].head(limit)

    def getScopusData(self, DOI):
        data = {}
        counter = 1
        size = len(DOI)
        for doi in DOI:
            print("Scraping", counter, "/", size)

            url = "https://api.elsevier.com/content/abstract/doi/" + str(doi)
            resp = requests.get(url, headers={'Accept': 'application/json', 'X-ELS-APIKey': self.scopus_api_key})

            if resp.status_code == 200:
                temp = resp.json()["abstracts-retrieval-response"]
                individual_scopus_id = temp["coredata"]["dc:identifier"]
                data[individual_scopus_id] = temp
            else:
                print("Error with DOI:", doi)

            counter += 1

        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)

    def run(self):
        if os.path.exists("data.json"):
            os.remove("data.json")

        args = ["User ID", "WOS", "DOI"]
        one_researcher = self.getDOIs(args, limit=1)

        self.getScopusData(one_researcher["DOI"])

    def testRun(self, SCOPUS_ID):
        url = ("https://api.elsevier.com/content/article/scopus_id/" + SCOPUS_ID)
        resp = requests.get(url, headers={'Accept': 'application/json', 'X-ELS-APIKey': self.scopus_api_key})
        with open('testRun.json', 'w') as outfile:
            json.dump(resp.json(), outfile)

obj = Scopus()
# obj.run()
obj.testRun('85079767316')




