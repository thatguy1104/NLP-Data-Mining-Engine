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
        module_data = []
        with open('MODULE_CATALOGUE/CS_courses.json') as json_file:
            data = json.load(json_file)
            counter = 0
            size_data = len(data['modules'])
            for i in data['modules']:
                print("scraping", counter, "/", size_data)
                counter += 1
                module_id = data['modules'][i]['module_id']
                module_name = data['modules'][i]['name'].lower().split(' ')
                module_name_joined = "-".join(module_name)
                link = self.initial_link + module_name_joined + "-" + module_id

                data_mod = self.get_module_data(link, module_id)
                title, mod_id, inf_v, name_lead, description = data_mod[0], data_mod[1], data_mod[2], data_mod[3], data_mod[4]
                module_data.append((title, mod_id, inf_v, name_lead, description))

        return module_data

    def get_module_data(self, link, module_id):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'lxml')
        
        if soup.find('h1', class_="heading") is not None:
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

            return (title, module_id, inf_v, name_lead, description)
        else:
            return (None, None, None, None, None)
        
    def writeData(self, all_data):
        data = {}
        for title, module_id, info, name_lead, description in all_data:
            if (title and module_id and info and name_lead and description) is not None:
                
                data[module_id] = {}
                data[module_id]['Title'] = title
                data[module_id]['Faculty'] = info[0]
                data[module_id]['Teaching Department'] = info[1]
                data[module_id]['Credit Value'] = info[2]
                data[module_id]['Module Leader'] = name_lead
                data[module_id]['Description'] = description

        with open('MODULE_CATALOGUE/one_module_data.json', 'a', encoding='utf8') as outfile:
            json.dump(data, outfile, ensure_ascii=False)

        print("written to one_module_data.json")

    def run(self):
        # self.getAllDepartments() # run once
        # self.get_CS_modules() # run once
        data = self.scrape_module()
        self.writeData(data)

        