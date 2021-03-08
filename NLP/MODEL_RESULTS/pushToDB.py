import sys
import json
import pyodbc
import datetime

# SERVER LOGIN DETAILS
server = 'miemie.database.windows.net'
database = 'MainDB'
username = 'miemie_login'
password = 'e_Paswrd?!'
driver = '{ODBC Driver 17 for SQL Server}'
curr_time = datetime.datetime.now()

# CONNECT TO DATABASE
myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server +';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

def progress(count, total, custom_text, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '*' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
    sys.stdout.flush()

def checkIfExists(primaryKey):
    cur = myConnection.cursor()
    cur.execute(
        "SELECT * FROM ModuleMappings WHERE Module_ID = (?)", (primaryKey))
    data = cur.fetchall()
    if len(data) == 0:
        return False
    return True

def pushToDB(data):
    cur = myConnection.cursor()
    # DO NOT WRITE IF LIST IS EMPTY DUE TO TOO MANY REQUESTS
    if not data:
        print("Data error")
    else:
        # EXECUTE INSERTION INTO DB
        insertion = """INSERT INTO ModuleMappings(Module_ID, SDG_1, SDG_2, SDG_3, SDG_4,
                                                  SDG_5, SDG_6, SDG_7, SDG_8, SDG_9, SDG_10,
                                                  SDG_11, SDG_12, SDG_13, SDG_14, SDG_15, 
                                                  SDG_16, SDG_17, Misc, Last_Updated) 
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        cur.execute(insertion, data)
    myConnection.commit()

def organiseSDG(content):
    sdgList = [0] * 18
    for elem in content:
        try:
            elem = int(elem)
            sdgList[elem] = 1
        except:
            pass
    return sdgList

def push():
    timestamp = datetime.datetime.now()
    counter = 1
    with open('NLP/MODEL_RESULTS/processed_results.json') as json_file:
        data = json.load(json_file)
        lenData = len(data)
        for module in data:
            progress(counter, lenData, "Pushing to ModuleMappings DB Table")
            if not checkIfExists(module):
                content = data[module]
                final_list = organiseSDG(content)
                final_list.insert(0, module)
                final_list.append(timestamp)
                final_list = tuple(final_list)
                pushToDB(tuple(final_list))
            counter += 1

push()
