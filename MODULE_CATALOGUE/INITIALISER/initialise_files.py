import requests
import json
import sys

class Initialiser():

    def __init__(self):
        self.__initial_link = "https://www.ucl.ac.uk/module-catalogue/modules/"
        self.__token = "uclapi-1e6c06cea59cf57-a6c4f5e96678dc2-4548665203179d6-765442292e213d7"

    def __init_Departments(self):
        params = {"token": self.__token}
        data = requests.get("https://uclapi.com/timetable/data/departments", params=params).json()
        with open('MODULE_CATALOGUE/INITIALISER/departments.json', 'w') as outfile:
            json.dump(data, outfile)
        print("Departments initialised")

    def __progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' %
                         (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __init_All_Module_Links(self):
        module_data = {}
        
        with open('MODULE_CATALOGUE/INITIALISER/departments.json') as json_file:
            data = json.load(json_file)['departments']

            for i in range(len(data)):
                self.__progress(i, len(data), "Modules initialised")
                data_to_pass = []
                # Construct a list for each department
                depID = data[i]['department_id']
                depName = data[i]['name']

                params = {"token": self.__token, "department": depID}
                resp = requests.get("https://uclapi.com/timetable/data/modules", params=params)

                valid = True
                try:
                    resp = resp.json()
                except:
                    valid = False

                if valid and resp is not None:
                    resp = resp['modules']
                    for j in resp:
                        moduleID = resp[j]['module_id']
                        moduleName_temp = resp[j]['name']
                        moduleName = resp[j]['name'].lower().split(' ')
                        module_name_joined = "-".join(moduleName)
                        link = self.__initial_link + module_name_joined + "-" + moduleID

                        module_data[moduleID] = {}
                        module_data[moduleID]['Department_ID'] = depID
                        module_data[moduleID]['Department_Name'] = depName
                        module_data[moduleID]['Module_ID'] = moduleID
                        module_data[moduleID]['Module_Name'] = moduleName_temp
                        module_data[moduleID]['Link'] = link

                        with open('MODULE_CATALOGUE/INITIALISER/all_module_links.json', 'w') as outfile:
                            json.dump(module_data, outfile)
        print()

    def initialiseAll(self):
        self.__init_Departments()
        self.__init_All_Module_Links()
