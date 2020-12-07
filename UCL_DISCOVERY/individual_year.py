import requests
from bs4 import BeautifulSoup

class IndividualYear:
    def __init__(self, link=None):
        self.link = "https://discovery.ucl.ac.uk/view/year/1956.html"
        self.paper_links = []

    def get_papers(self):
        response = requests.get(self.link)
        soup = BeautifulSoup(response.text, 'lxml')

        div = soup.find('div', class_='ep_view_page ep_view_page_view_year')
        rows = div.findAll('tr')

        for tr in rows:
            col = tr.find('td')
            link = col.find('a').get('href')
            self.paper_links.append(link)

    def print_links(self):
        for link in self.paper_links:
            print(link);

    def run(self):
        self.get_papers()
        self.print_links()