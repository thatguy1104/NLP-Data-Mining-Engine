import sys
import json
import psycopg2
import pymongo
import ssl
from bson import json_util
from colorsys import hsv_to_rgb
from typing import Tuple

lda_threshold = svm_threshold = 30

class Synchronizer():
    
    def __init__(self):
        self.host = "mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(self.host)

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

    def __getModulePrediction(self, limit: int = None) -> dict:
        db = self.client.Scopus
        col = db.ModulePrediction
        data = col.find().limit(limit)
        del data[0]['_id']
        return data[0]

    def __getModuleValidation(self, limit: int = None) -> dict:
        db = self.client.Scopus
        col = db.ModuleValidation
        data = col.find().limit(limit)
        del data[0]['_id']
        return data[0]

    def __acquireData(self, pubPred, svmSdgPred, scopVal, ihePred, modPred, modVal, limit: int) -> Tuple[dict, dict, dict, dict]:
        scopusPrediction_path = "PublicationPrediction"
        svm_sdg_predictions_path = "SvmSdgPredictions"
        scopusValidationSDG_path = "ScopusValidation"
        iheScopusPrediction_path = "IHEPrediction"
        data_, svm_predictions, scopusValidation, ihePrediction, module_predictions, module_val = [], [], [], [], [], []

        if pubPred:
            data_ = self.__getPublicationPrediction(limit)
            print("Acquired scopus predictions")
        if svmSdgPred:
            svm_predictions = self.__getSvmSdgPredictions(limit)
            print("Acquired svm sdg predictions")
        if scopVal:
            scopusValidation = self.__getScopusValidation(limit)
            print("Acquired scopus validation")
        if ihePred:
            ihePrediction = self.__getIHEPrediction(limit)
            print("Acquired ihe predictions")
        if modPred:
            module_predictions = self.__getModulePrediction(limit)
            print("Acquired module predictions")
        if modVal:
            module_val = self.__getModuleValidation(limit)
            print("Acquired module validation")

        return data_, svm_predictions, scopusValidation, ihePrediction, module_predictions, module_val

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
        lst = data_['Document Topics'][publication]
        result = [0] * len(lst)
        
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

    def __update_postgres_data_publications(self, data_sdg:dict, title:str) -> None:
        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()
        
        cur.execute(
            'UPDATE public.app_publication SET \"assignedSDG\" = \'{}\' WHERE title = \'{}\''.format(json.dumps(data_sdg), title.replace("'", "''"))
        )
        con.commit()
        cur.close()

    def __update_postgres_data_modules(self, data_sdg: dict, module_id: str) -> None:
        con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie',
                               host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
        cur = con.cursor()
        cur.execute(
            'UPDATE public.app_module SET \"assignedSDG\" = \'{}\' WHERE "Module_ID" = \'{}\''.format(json.dumps(data_sdg), module_id)
        )
        con.commit()
        cur.close()

    def __loadSDG_Data_PUBLICATION(self, limit) -> None:
        data_, svm_predictions, scopusValidation, ihePrediction, module_predictions, module_validation = self.__acquireData(True, True, True, True, False, False, limit)
        count = 1
        l = len(data_)
        print()

        for i in data_:
            self.__progress(count, l, "synching Publications SDG + IHE with Django")
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

                self.__update_postgres_data_publications(publication_SDG_assignments, data_[i]['Title'])
        print()

    def __loadSDG_Data_MODULES(self, limit) -> None:
        data_, svm_predictions, scopusValidation, ihePrediction, module_predictions, module_validation = self.__acquireData(False, True, False, False, True, True, limit)
        count, l = 1, len(module_predictions['Document Topics'])
        print()

        for module in module_predictions['Document Topics']:
            self.__progress(count, l, "synching Module SDG with Django")
            weights = module_predictions['Document Topics'][module]
            module_SDG_assignments = {}
            module_SDG_assignments["Module_ID"] = module

            similarityRGB = module_validation[module]['Similarity']
            module_validation[module]['ColorRed'], module_validation[module]['ColorGreen'], module_validation[module]['ColorBlue'] = self.__pseudocolor(similarityRGB*100, 0, 100)
            module_validation[module]['StringCount'] = self.__normalise(module_validation[module]['SDG_Keyword_Counts'])

            module_SDG_assignments["Validation"] = module_validation[module]
            
            w = []
            for i in range(len(weights)):
                weights[i] = weights[i].replace('(', '').replace(')', '').replace('%', '').replace(' ', '').split(',')
                sdgNum = weights[i][0]
                module_SDG_assignments[sdgNum] = float(weights[i][1])
                w.append((sdgNum, float(weights[i][1])))

            if module_SDG_assignments["Validation"]:
                module_SDG_assignments['ModelResult'] = ",".join(self.__thresholdAnalyse(w, threshold=lda_threshold))
                normalised = self.__normalise(module_SDG_assignments["Validation"]['SDG_Keyword_Counts'])
                module_SDG_assignments['StringResult'] = ",".join(self.__thresholdAnalyse(normalised, threshold=lda_threshold))
                module_SDG_assignments['SVM'], module_SDG_assignments['SVM_Prediction'] = self.__getSVM_predictions(svm_predictions['Module'], module)

                self.__update_postgres_data_modules(module_SDG_assignments, module)
            count += 1
        print()


    def run(self, limit):
        self.__loadSDG_Data_PUBLICATION(limit)
        self.__loadSDG_Data_MODULES(limit)
        self.client.close()
