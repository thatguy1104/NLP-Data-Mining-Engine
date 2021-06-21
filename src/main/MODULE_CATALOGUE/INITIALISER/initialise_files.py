import requests
import json
import sys

class Initialiser():

    def __init__(self):
        self.__initial_link = "https://www.ucl.ac.uk/module-catalogue/modules/" # UCL Module catalogue link
        self.token = "uclapi-1e6c06cea59cf57-a6c4f5e96678dc2-4548665203179d6-765442292e213d7" # UCL API token

    def __init_Departments(self) -> None:
        """
            Make a request to the UCL API for departmental data.
            Populate <departments.json> files
        """

        params = {"token": self.token}
        data = requests.get("https://uclapi.com/timetable/data/departments", params=params).json()
        with open('src/main/MODULE_CATALOGUE/INITIALISER/departments.json', 'w') as outfile:
            json.dump(data, outfile)
        print("Departments initialised")

    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __init_All_Module_Links(self) -> None:
        """
            Using <departments.json> compute a link for each module
            Use BeautifulSoup to compute a link for each module from the catalogue
            Write results to <all_module_links.json>
        """

        module_data = {}
        with open('src/main/MODULE_CATALOGUE/INITIALISER/departments.json') as json_file:
            data = json.load(json_file)['departments']

            for i in range(len(data)):
                self.__progress(i, len(data), "Modules initialised")
                data_to_pass = []
                depID = data[i]['department_id'] # Construct a list for each department
                depName = data[i]['name']

                params = {"token": self.token, "department": depID}
                resp = requests.get("https://uclapi.com/timetable/data/modules", params=params)
                
                valid = True
                try:
                    resp = resp.json()
                except:
                    valid = False # flag response as invalid

                if valid and resp is not None:
                    resp = resp['modules']
                    for j in resp:
                        moduleID = resp[j]['module_id']
                        moduleName_temp = resp[j]['name']
                        moduleName = resp[j]['name'].lower().split(' ')
                        module_name_joined = "-".join(moduleName)
                        link = self.__initial_link + module_name_joined + "-" + moduleID # compose a unique module catalogue link

                        module_data[moduleID] = {}
                        module_data[moduleID]['Department_ID'] = depID
                        module_data[moduleID]['Department_Name'] = depName
                        module_data[moduleID]['Module_ID'] = moduleID
                        module_data[moduleID]['Module_Name'] = moduleName_temp
                        module_data[moduleID]['Link'] = link

                        # Record the data in a JSON file
                        with open('src/main/MODULE_CATALOGUE/INITIALISER/all_module_links.json', 'w') as outfile:
                            json.dump(module_data, outfile)
        print()

    def initialiseAll(self) -> None:
        """
            Controller function for self
            Initialise departmental data, then module links in preparation for scraping
        """
        
        self.__init_Departments()
        self.__init_All_Module_Links()
