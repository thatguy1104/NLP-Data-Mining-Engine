import requests
import json
from bs4 import BeautifulSoup
import lxml
import pyodbc
import datetime


class IndividualPaper:
    def __init__(self, link=None):
        self.link = 'https://discovery.ucl.ac.uk/id/eprint/1475882/'
        self.all_links = []
        self.title = ""
        self.headers = {}
        self.data = {}

    def get_data(self):
        response = requests.get(self.link)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # EXTRACT TITLE
        ok = soup.find('div', class_='padding')
        title = soup.findAll('h2')[0].text.replace('\t', '').replace('\n', '').split(' ')  # Clean up data from empty strings and NoneTypes
        title = list(filter(None, title))
        title = ' '.join(map(str, title))
        self.data['Title'] = title

        # EXTRACT ABSTRACT
        abstrct = soup.find('div', class_='ep_summary_content_main').findAll('p')[1].text
        self.data['Abstract'] = abstrct

        # EXTRACT REST OF THE DATA
        main = soup.find('div', class_='ep_summary_content_main')
        tr = main.findAll('tr')

        table_headers = {}
        for elem in tr:
            column = elem.find('th')
            txt = elem.find('td').text.replace('\t', '').replace('\n', '').split(' ') # Clean up data from empty strings and NoneTypes
            txt = list(filter(None, txt))
            txt = ' '.join(map(str, txt))

            if column is not None:
                column = elem.find('th').text
                self.data[column] = txt

    def write_to_JSON(self):
        with open('UCL_DISCOVERY/individual_data.json', 'w', encoding='utf8') as outfile:
            json.dump(self.data, outfile, ensure_ascii=False)
            print("Written")
            
    def run(self):
        self.get_data()
        self.write_to_JSON()
        
