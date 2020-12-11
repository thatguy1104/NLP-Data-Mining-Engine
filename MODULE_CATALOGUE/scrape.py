import re
import sys
import requests
import json
from bs4 import BeautifulSoup
import lxml
import time
import pyodbc
import datetime

class UCL_Module_Catalogue():

    def __init__(self):
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'
    
    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def scrape_modules(self):
        module_data = []
        curr_time = datetime.datetime.now()
        with open('MODULE_CATALOGUE/INITIALISER/all_module_links.json') as json_file:
            data = json.load(json_file)
            lim = 0
            l = len(data)
            for i in data:
                self.progress(lim, l, "Scraping for ModuleData")
                module_data = []
                # if lim < 40:
                depName = data[i]['Department_Name']
                depID = data[i]['Department_ID']
                moduleName = data[i]['Module_Name']
                moduleID = data[i]['Module_ID']
                catalogueLink = data[i]['Link']
                
                title, mod_id, fac, dep, cred_val, name_lead, description = self.get_module_data(catalogueLink, moduleID)
                if title is not None:
                    module_data.append((depName, depID, moduleName, moduleID, fac, cred_val, name_lead, catalogueLink, description, curr_time))
                    self.writeData_DB(module_data)

                lim += 1

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

        if not self.checkTableExists(myConnection, "ModuleData"):
            # EXECUTE SQL COMMANDS
            cur.execute("DROP TABLE IF EXISTS ModuleData;")
            create = """CREATE TABLE ModuleData(
                Department_Name      VARCHAR(150),
                Department_ID        VARCHAR(150),
                Module_Name          VARCHAR(150),
                Module_ID            VARCHAR(150),
                Faculty              VARCHAR(100),
                Credit_Value         INT,
                Module_Lead          VARCHAR(100),
                Catalogue_Link       VARCHAR(150),
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
            insertion = "INSERT INTO ModuleData(Department_Name, Department_ID, Module_Name, Module_ID, Faculty, Credit_Value, Module_Lead, Catalogue_Link, Description, Last_Updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.executemany(insertion, all_data)

            # print("Successully written to table <ModuleData> (db: {0})".format(self.database))

        myConnection.commit()
        myConnection.close()

    def run(self):
        self.scrape_modules()
        print("Successully written to table <ModuleData> (db: {0})".format(self.database))
        # self.writeData_DB(data)
