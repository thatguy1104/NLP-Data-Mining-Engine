import json
import pymongo
import psycopg2
import ssl
from bson import json_util
from colorsys import hsv_to_rgb
from typing import Tuple

lda_threshold = svm_threshold = 30

class Synchronizer():
    
    def __init__(self):
        self.host = "mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(self.host)

    def __getPublicationPrediction(self, limit:int = None) -> dict:
        db = self.client.Scopus
        col = db.PublicationPrediction
        data = col.find().limit(limit)
        # Process mongodb response to a workable dictionary format.
        result = {}
        for publication in data:
            del publication['_id']
            result[publication['DOI']] = publication
        return result
    
    def __getSvmSdgPredictions(self, limit: int = None) -> dict:
        db = self.client.Scopus
        col = db.SvmSdgPredictions
        data = col.find().limit(limit)
        # Process mongodb response to a workable dictionary format.
        # i = json.loads(json_util.dumps(data))
        # return i
        del data[0]['_id']
        return data[0]

    def __getScopusValidation(self, limit: int = None) -> dict:
        db = self.client.Scopus
        col = db.ScopusValidation
        data = col.find().limit(limit)
        del data[0]['_id']
        return data[0]

    def __getIHEPrediction(self, limit: int = None) -> dict:
        db = self.client.Scopus
        col = db.IHEPrediction
        data = col.find().limit(limit)
        del data[0]['_id']
        return data[0]

    def __acquireData(self, limit: int) -> Tuple[dict, dict, dict, dict]:
        scopusPrediction_path = "PublicationPrediction"
        svm_sdg_predictions_path = "SvmSdgPredictions"
        scopusValidationSDG_path = "ScopusValidation"
        iheScopusPrediction_path = "IHEPrediction"

        data_ = self.__getPublicationPrediction(limit)
        print("Acquired scopus predictions")
        svm_predictions = self.__getSvmSdgPredictions(limit)
        print("Acquired svm sdg predictions")
        scopusValidation = self.__getScopusValidation(limit)
        print("Acquired scopus validation")
        ihePrediction = self.__getIHEPrediction(limit)
        print("Acquired ihe predictions")

        # return data_
        return data_, svm_predictions, scopusValidation, ihePrediction

    def __pseudocolor(self, val: float, minval: int, maxval: int) -> Tuple[int, int, int]:
        h = (float(val-minval) / (maxval-minval)) * 120
        r, g, b = hsv_to_rgb(h/360, 1., 1.)
        oldRange = 1
        newRange = 255
        r = int(((r) * newRange / oldRange))
        g = int(((g) * newRange / oldRange))
        b = int(((b) * newRange / oldRange))
        return r, g, b
    
    def __normalise(self, lst: list) -> list:
        result = [0]*18
        sum_ = sum(lst)
        for i in range(len(lst)):
            if sum_ != 0:
                result[i] = (str(i+1), (lst[i] / sum_) * 100)
            else:
                result[i] = (str(i+1), 0.0)
        return result

    def __getPublication_validation(self, data_: dict, publication: dict) -> dict:
        similarityRGB = data_[publication]['Similarity']
        data_[publication]['ColorRed'], data_[publication]['ColorGreen'], data_[publication]['ColorBlue'] = self.__pseudocolor(similarityRGB*100, 0, 100)
        data_[publication]['StringCount'] = self.__normalise(data_[publication]['SDG_Keyword_Counts'])
        return data_[publication]

    def __getThreshold(self, result: list, threshold: int) -> list:
        validPerc = []
        for i in range(len(result)):
            if result[i] >= threshold:
                validPerc.append(str(i + 1))
        return validPerc

    def __getIHE_predictions(self, data_: dict, publication: dict) -> Tuple[list, str]:
        result = [0] * 9
        lst = data_['Document Topics'][publication]
        for i in lst:
            cleaner = i.replace("(", "").replace(")", "").replace("%", "").split(',')
            topic_num = int(cleaner[0])
            percentage = float(cleaner[1])
            result[topic_num - 1] = percentage

        validPerc = self.__getThreshold(result, lda_threshold)
        validPerc = ",".join(validPerc)
        return result, validPerc

    def __truncate(self, n:float, decimals:int =0) -> float:
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    def __getSVM_predictions(self, data, element) -> Tuple[list, str]:
        result_array = [0] * 18
        validPerc = ""

        if element in data:
            for i in range(len(data[element])):
                if isinstance(data[element][i], float):
                    weight = self.__truncate(data[element][i] * 100, 1)
                else:
                    weight = self.__truncate(float(data[element][i]) * 100, 1)
                result_array[i] = weight

            validPerc = self.__getThreshold(result_array, svm_threshold)
            validPerc = ",".join(validPerc)
        return result_array, validPerc

    def __thresholdAnalyse(self, lst, threshold):
        validWeights = []
        p = sorted(lst, key=lambda x: x[1])
        for sdg, weight in p:
            if weight >= threshold:
                validWeights.append(sdg)
        return validWeights

    def __getPostgres_modules(self, title:str):
        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()
        cur.execute("""select id, title, data, "assignedSDG" from public."app_publication" where title = '""" + title + "'")
        result = cur.fetchall()
        con.close()
        return result[0]

    def __create_column_postgres_table(self):
        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()
        cur.execute("""ALTER TABLE public."app_publication" ADD COLUMN IF NOT EXISTS assignedSDG jsonb;""")
        con.commit()
        con.close()

    def __update_postgres_data(self, data_sdg:dict, title:str) -> None:
        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()
        print(str(data_sdg))
        test_string = str(data_sdg)

        #Replace some instances of the single quotes in the JSON file to 2* single quotes so it can be parsed by PostgreSQL
        cur.execute(
            'UPDATE public.app_publication SET \"assignedSDG\" = \'{}\' WHERE title = \'{}\''.format(json.loads(json.dumps("\"" + str(data_sdg).replace("{'", "{''").replace("': '", "'': ''").replace("', '", "'', ''").replace("': {", "'': {").replace("Similarity'", "Similarity''").replace("'SDG_Keyword_Counts'", "''SDG_Keyword_Counts''").replace("'ColorRed'", "''ColorRed''").replace("'ColorGreen'", "''ColorGreen''").replace("'ColorBlue'", "''ColorBlue''").replace("'StringCount'", "''StringCount''").replace("'ModelResult'", "''ModelResult'").replace("''IHE'", "''IHE''").replace("'IHE_Prediction'", "''IHE_Prediction'").replace("''SVM'", "''SVM''").replace("'SVM_Prediction'", "''SVM_Prediction'").replace("'''}", "''''}") + "\"")), title)
        )

        con.commit()

        cur.close()

    def __loadSDG_Data_PUBLICATION(self) -> None:
        data_, svm_predictions, scopusValidation, ihePrediction = self.__acquireData(limit=1)
        count = 1
        
        for i in data_:
            # print("Writing", count, "/", len(data_))
            count += 1
            publication_SDG_assignments = data_[i]
            calc_highest = []
            for j in range(18):
                try:
                    weight = float(i[str(j)]) * 100
                    weight = round(weight, 2)
                    calc_highest.append((str(j), weight))
                except:
                    pass

            p = sorted(calc_highest, key=lambda x: x[1])
            validWeights = []
            for sdg, weight in p:
                if weight >= lda_threshold:
                    validWeights.append(sdg)

            publication_SDG_assignments['DOI'] = i
            publication_SDG_assignments["Validation"] = self.__getPublication_validation(scopusValidation, i)
            publication_SDG_assignments['ModelResult'] = ",".join(validWeights)
            publication_SDG_assignments['IHE'], publication_SDG_assignments['IHE_Prediction'] = self.__getIHE_predictions(ihePrediction, i)
            publication_SDG_assignments['SVM'], publication_SDG_assignments['SVM_Prediction'] = self.__getSVM_predictions(svm_predictions['Publication'], i)

            if publication_SDG_assignments["Validation"]['SDG_Keyword_Counts']:
                normalised = self.__normalise(publication_SDG_assignments["Validation"]['SDG_Keyword_Counts'])
                publication_SDG_assignments['StringResult'] = ",".join(self.__thresholdAnalyse(normalised, threshold=lda_threshold))

                postgre_publication = self.__getPostgres_modules(title=data_[i]['Title'])
                if len(postgre_publication) < 4:
                    self.__create_column_postgres_table()

                # with open('oke.json', 'w') as outfile:
                #     json.dump(publication_SDG_assignments, outfile)
                #     return
                # self.__update_postgres_data(publication_SDG_assignments, data_[i]['Title'])

            # print(i['Title'])
            # self.__update_postgres_data(publication_SDG_assignments, data_[i]['Title'])

    def run(self):
        # self.__loadSDG_Data_PUBLICATION()
        t = "Outcomes following surgery in subgroups of comatose and very elderly patients with chronic subdural hematoma"
        publ = self.__getPostgres_modules(title=t)
        print(len(publ))
        id_, title, data, assigned = publ[0], publ[1], publ[2], publ[3]
        print(publ[3])


        with open('oke.json') as f:
            r = json.load(f)
        
        self.__update_postgres_data(r, t)

        self.client.close()


obj = Synchronizer()
obj.run()
