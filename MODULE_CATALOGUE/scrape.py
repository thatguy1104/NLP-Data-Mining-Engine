import re
import requests
import json
from bs4 import BeautifulSoup
import lxml
import time
import pyodbc
import datetime

class UCL_Module_Catalogue():

    def __init__(self):
        self.initial_link = "https://www.ucl.ac.uk/module-catalogue/modules/"
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'
    
    def scrape_module(self, data):
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

            # PARSE: module title
            title = soup.find('h1', class_="heading").text

            # PARSE: faculty, department, credit value
            key_info_left = soup.find('dl', class_="dl-inline")
            inf_t = []
            info_titles = key_info_left.findAll('dt')
            inf_v = []
            info_values = key_info_left.findAll('dd')
            
            for t in info_titles:
                inf_t.append(t.text)
            for v in info_values:
                inf_v.append(v.text)

            # PARSE: description section
            result_description = ""
            description = soup.find('div', class_="module-description")
            description_1 = description.findAll('p')
            description_2 = description.findAll('li')

            for d in description_1:
                result_description += d.text.replace('\n', '').replace('\t', '')
            for d2 in description_2:
                result_description += d2.text.replace('\n', '').replace('\t', '')

            # Clean up the description string
            result_description = re.sub("[^a-zA-Z]", " ", result_description).split(' ')
            result_description = list(filter(None, result_description))
            result_description = ' '.join(map(str, result_description))

            # PARSE: module lead name
            module_lead = soup.findAll('dl', class_="dl-inline")[3]
            name_lead = module_lead.findAll('dd')[1].text.replace('\n', '').split(' ')
            name_lead = list(filter(None, name_lead))
            name_lead = ' '.join(map(str, name_lead))

            return (title, module_id, inf_v[0], inf_v[1], int(inf_v[2]), name_lead, result_description)
        else:
            return (None, None, None, None, None, None, None)

    def checkTableExists(self, dbcon, tablename):
        dbcur = dbcon.cursor()
        dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

    def writeData_DB(self, all_data):
        # all_data = [(...), (...), (...)]

        # CONNECT TO DATABASE
        myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        cur = myConnection.cursor()

        # if not self.checkTableExists(myConnection, "ModuleData"):
        # EXECUTE SQL COMMANDS
        cur.execute("DROP TABLE IF EXISTS ModuleData;")
        create = """CREATE TABLE ModuleData(
            Module_ID            VARCHAR(150),
            Module_Title         VARCHAR(150),
            Faculty              VARCHAR(100),
            Department           VARCHAR(100),
            Credit_Value         INT,
            Module_Lead          VARCHAR(100),
            Description          VARCHAR(MAX),
            Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP
        );"""
        cur.execute(create)
        myConnection.commit()
        print("Successully created table <ModuleData>")

        # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
        if not all_data:
            print("Not written --> too many requests")
        else:
            # EXECUTE INSERTION INTO DB
            cur.fast_executemany = False
            insertion = "INSERT INTO ModuleData(Module_ID, Module_Title, Faculty, Department, Credit_Value, Module_Lead, Description, Last_Updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cur.executemany(insertion, all_data)

            print("Successully written to table <ModuleData> (db: {0})".format(self.database))

        myConnection.commit()
        myConnection.close()

    def run(self):
        """
            Gets all departments and their modules
            Stores in all_module_links.json
            self.get_department()
        """

        # data = self.scrape_module('SOCSC_IOE')
        # self.writeData_DB(data)
