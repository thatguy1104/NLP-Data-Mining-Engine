import requests
import json
from bs4 import BeautifulSoup
import lxml
import pyodbc
import datetime

class UCL_Discovery:
    def __init__(self):
        self.link = 'https://discovery.ucl.ac.uk/view/year/'
        self.all_links = []
        

    def get_all_years(self):
        response = requests.get(self.link)
        soup = BeautifulSoup(response.text, 'lxml')
        columns = soup.findAll('td')

        for col in columns:
            row = col.findAll('a')
            for val in row:
                data_link = val['href']
                self.all_links.append(self.link + data_link)

    def get_page_data(self, link):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        div = soup.find('div', class_='ep_view_page ep_view_page_view_year')
        print(div)
        

    def total_links(self):
        for i in self.all_links:
            self.get_page_data(i)
            break
            

    def run(self):
        self.get_all_years()
        self.total_links()
