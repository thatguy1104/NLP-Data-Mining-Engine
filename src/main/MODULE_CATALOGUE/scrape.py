import re
import sys
import requests
import json
from bs4 import BeautifulSoup
import lxml
import time
import pyodbc
import datetime
import smtplib
from typing import Tuple, Optional

class UCL_Module_Catalogue():

    def __initialise_db_connection(self):
        # SERVER LOGIN DETAILS
        self.server = 'summermiemieservver.database.windows.net'
        self.database = 'summermiemiedb'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'

        # CONNECT TO DATABASE
        return pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        
    
    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60 # size of the progress bar on the commandline
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __checkIfExists(self, primaryKey: str) -> bool:
        """
            Check whether a record for a given module exists in <Module_ID> database table
        """
        myConnection = self.__initialise_db_connection()
        cur = myConnection.cursor()
        cur.execute("SELECT * FROM ModuleData WHERE Module_ID = (?)", (primaryKey))
        data = cur.fetchall()
        if len(data) == 0:
            myConnection.close()
            return False
        myConnection.close()
        return True

    def __scrape_modules(self) -> None:
        """
            Abstracted manager for scraping module data from UCL Module Catalogue.
            Organizes scraped data into appropriate structrure.
            Pushes data to Azure SQL Server
        """

        module_data = []
        curr_time = datetime.datetime.now()
        with open('src/main/MODULE_CATALOGUE/INITIALISER/all_module_links.json') as json_file:
            data = json.load(json_file)
            lim = 0
            l = len(data)
            for i in data:
                self.progress(lim, l, "Scraping for ModuleData") # visualise progress bar in the commandline
                module_data = []
                depName = data[i]['Department_Name']
                depID = data[i]['Department_ID']
                moduleName = data[i]['Module_Name']
                moduleID = data[i]['Module_ID']
                catalogueLink = data[i]['Link']

                if not self.__checkIfExists(moduleID):
                    title, mod_id, fac, dep, cred_val, name_lead, description = self.get_module_data(catalogueLink, moduleID)
                    try:
                        cred_val = int(cred_val)
                    except:
                        cred_val = None # if credit value is missing, mark as None
                    if title is not None:
                        # Organise module data into a list of tuples (format for writing to database)
                        module_data.append((depName, depID, moduleName, moduleID, fac, cred_val, name_lead, catalogueLink, description, curr_time))
                        self.__writeData_DB(module_data)

                lim += 1

    def get_module_data(self, link: str, module_id: str) -> Optional[Tuple[str, str, str, str, str, str, str]]:
        """
            Uses Beautiful soup to scrape data from module catalogue.
            Clean, process and organise data fields into appropriate data structure.
            Error prone, some fields may vary or be absent
        """
        
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
            if description is not None:
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

            else:
                result_description = None

            # PARSE: module lead name
            module_lead = soup.findAll('dl', class_="dl-inline")
            if module_lead is not None and len(module_lead) > 3:
                name_lead = module_lead[3].findAll('dd')[1].text.replace('\n', '').split(' ')
                name_lead = list(filter(None, name_lead))
                name_lead = ' '.join(map(str, name_lead))
            else:
                name_lead = None

            return (title, module_id, inf_v[0], inf_v[1], inf_v[2], name_lead, result_description)
        else:
            return (None, None, None, None, None, None, None) # no data present for a given link

    def __writeData_DB(self, all_data: list) -> None:
        """
            Push a single module data to <ModuleData> database table.
            Data has to retain integrity (10 elements in a tuple: str, str, str, str, str, int, str, str, str, timestamp)
        """
        myConnection = self.__initialise_db_connection()
        cur = myConnection.cursor()
        if not all_data:
            print("Not written --> too many requests") # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
        else:
            # Execute insertion into database table <ModuleData>
            insertion = "INSERT INTO ModuleData(Department_Name, Department_ID, Module_Name, Module_ID, Faculty, Credit_Value, Module_Lead, Catalogue_Link, Module_Description, Last_Updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.executemany(insertion, all_data)

        myConnection.commit()
        myConnection.close()
        
    def run(self) -> None:
        """
            Controller method for self
            Organises scraping & database pushing
        """
        
        self.__scrape_modules()
        print("Successully written to table <ModuleData> (db: {0})".format(self.database))
