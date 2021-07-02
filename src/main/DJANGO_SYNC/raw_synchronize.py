import pymongo
import psycopg2
import pyodbc
import json
import sys

class RawSynchronizer():

    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %
                         (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __get_mysql_module_data(self) -> list:
        server = 'summermiemieservver.database.windows.net'
        database = 'summermiemiedb'
        username = 'miemie_login'
        password = 'e_Paswrd?!'
        driver = '{ODBC Driver 17 for SQL Server}'
        myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server +';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        curr = myConnection.cursor()
        curr.execute("SELECT * FROM [dbo].[ModuleData]")
        return curr.fetchall()

    def __update_module_from_mysql(self) -> None:
        data = self.__get_mysql_module_data()
        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()
        c = 1
        for i in data:
            self.__progress(c, len(data), "Syncing scraped modules to Django")
            query = """INSERT INTO public.app_module (Department_Name,Department_ID,Module_Name,Module_ID,Faculty,Credit_Value,Module_Lead,Catalogue_Link,Description)
                       VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}') ON CONFLICT (Module_ID) DO NOTHING""".format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
            con.commit()
            c += 1
        cur.close()

    def __update_publications_from_mongo(self) -> None:
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.Data
        data = col.find(batch_size=10)

        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()

        c, l = 0, 100000
        for i in data:
            self.__progress(c, l, "Syncing scraped publications to Django")
            del i['_id']
            title = i['Title'] = i['Title'].replace("\'", "\'\'")

            if i['Abstract']:
                i['Abstract'] = i['Abstract'].replace("\'", "\'\'")
            if i['Source']:
                i['Source'] = i['Source'].replace("\'", "\'\'")
            if i['AuthorData']:
                for key, val in i['AuthorData'].items():
                    if val['Name']:
                        val['Name'] = val['Name'].replace("\'", "\'\'")
                    if val['AffiliationName']:
                        val['AffiliationName'] = val['AffiliationName'].replace("\'", "\'\'")
            if i['IndexKeywords']:
                for index, val in enumerate(i['IndexKeywords']):
                    i['IndexKeywords'][index] = val.replace("\'", "\'\'")
            if i['AuthorKeywords']:
                for index, val in enumerate(i['AuthorKeywords']):
                    i['AuthorKeywords'][index] = val.replace("\'", "\'\'")

            blank_dict = {
            '1': '', '2': '', '3': '', '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': '', '10': '', '11': '', '12': '',
            '13': '', '14': '', '15': '', '16': '', '17': '', '18': '',
            'DOI': '',
            'IHE': [],
            'SVM': [],
            'Title': '',
            'Validation': {
                'ColorRed': 0, 'ColorBlue': 0, 'ColorGreen': 0, 'Similarity': 0,
                'StringCount': [['1', 0.0], ['2', 0.0], ['3', 0.0], ['4', 0.0], ['5', 0.0], ['6', 0.0],
                    ['7', 0.0], ['8', 0.0], ['9', 0.0], ['10', 0.0], ['11', 0.0], ['12', 0.0],
                    ['13', 0.0], ['14', 0.0], ['15', 0.0], ['16', 0.0], ['17', 0.0], ['18', 0.0]],
                'SDG_Keyword_Counts': []
                },
            'ModelResult': '',
            'StringResult': '',
            'IHE_Prediction': '',
            'SVM_Prediction': ''
        }

            query = """INSERT INTO public.app_publication (title, data, \"assignedSDG\") VALUES ('{0}', '{1}', '{2}') ON CONFLICT (title) DO NOTHING""".format(title, json.dumps(i), json.dumps(blank_dict))
            cur.execute(query)
            con.commit()
            c += 1
        print()
        client.close()
        con.close()

    def run(self):
        self.__update_publications_from_mongo()
        self.__update_module_from_mysql()
