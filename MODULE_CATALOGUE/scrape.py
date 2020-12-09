import requests
import json
from bs4 import BeautifulSoup
import lxml
import pyodbc
import datetime

class UCL_Module_Catalogue():

    def __init__(self):
        self.initial_link = "https://www.ucl.ac.uk/module-catalogue/modules/"
        self.module_link = "https://www.ucl.ac.uk/module-catalogue/modules/algorithms-COMP0005"
        self.token = "uclapi-1e6c06cea59cf57-a6c4f5e96678dc2-4548665203179d6-765442292e213d7"
    
    def getAllDepartments(self):
        params = {"token": self.token}
        r = requests.get("https://uclapi.com/timetable/data/departments", params=params).json()
        
        with open('MODULE_CATALOGUE/departments.json', 'w') as outfile:
            json.dump(r, outfile)
        
    def get_CS_modules(self):
        params = {"token": self.token, "department": "COMPS_ENG"}
        r = requests.get("https://uclapi.com/timetable/data/modules", params=params).json()

        with open('MODULE_CATALOGUE/CS_courses.json', 'w') as outfile:
            json.dump(r, outfile)

    def scrape_module(self):
        with open('MODULE_CATALOGUE/CS_courses.json') as json_file:
            data = json.load(json_file)

            for i in data['modules']:
                module_id = data['modules'][i]['module_id']
                module_name = data['modules'][i]['name'].lower().split(' ')
                module_name_joined = "-".join(module_name)
                link = self.initial_link + module_name_joined + "-" + module_id

        self.get_module_data("https://www.ucl.ac.uk/module-catalogue/modules/intelligent-systems-COMP0014", module_id)
                # self.get_module_data(link)

    def get_module_data(self, link, module_id):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        
        title = soup.find('h1', class_="heading").text

        key_info_left = soup.find('dl', class_="dl-inline")
        
        inf_t = []
        info_titles = key_info_left.findAll('dt')
        inf_v = []
        info_values = key_info_left.findAll('dd')
        
        for t in info_titles:
            inf_t.append(t.text)
        for v in info_values:
            inf_v.append(v.text)

        description = soup.find('div', class_="module-description").find('p').text.replace('\n', '')

        module_lead = soup.findAll('dl', class_="dl-inline")[3]
        name_lead = module_lead.findAll('dd')[1].text.replace('\n', '').split(' ')
        name_lead = list(filter(None, name_lead))
        name_lead = ' '.join(map(str, name_lead))

        self.writeData(title, module_id, inf_v, name_lead, description)
        
    def writeData(self, title, module_id, info, name_lead, description):
        data = {}
        data[module_id] = []

        data[module_id].append({
            'Title' : title,
            'Faculty': info[0],
            'Teaching Department': info[1],
            'Credit Value': info[2],
            'Module Leader' : name_lead,
            'Description' : description
        })

        with open('MODULE_CATALOGUE/one_module_data.json', 'w') as outfile:
            json.dump(data, outfile)
        print("written to one_module_data.json")

    def run(self):
        # self.getAllDepartments() # run once
        # self.get_CS_modules() # run once
        self.scrape_module()

        