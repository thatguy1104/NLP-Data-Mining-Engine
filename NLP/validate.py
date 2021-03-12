import numpy as np
import pandas as pd
import json
import re
import pymongo

matchedModulesSDG_filepath = "MODULE_CATALOGUE/matchedModulesSDG.json"
matchedPublicationsSDG_filepath = "SCOPUS/matchedScopusSDG.json"
num_of_sdgs = 18

class ValidateLDA():
    # SCOPUS MODEL
    def __read_scopus_sdg_model_data(self):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.PublicationPrediction
        data = col.find()

        # with open('NLP/MODEL_RESULTS/scopus_prediction_results.json', 'rb') as json_file:
        #     data = json.load(json_file)
        results = {}
        counter = 0
        for doi in data:
            weights = [0] * num_of_sdgs
            sdg_predictions = data[doi]
            for i in range(num_of_sdgs):
                sdg = str(i + 1)
                try:
                    w = float(sdg_predictions[sdg])
                except:
                    w = 0.0
                weights[i] = w
                results[doi] = weights
        client.close()
        return results

    # SCOPUS COUNT
    def __read_scopus_sdg_count_data(self):
        with open('SCOPUS/matchedScopusSDG.json', 'rb') as json_file:
            data = json.load(json_file)
            results = {} # dictionary with doi and SDG keyword counts.
            for doi, publication_sdgs_dict in data.items():
                sdg_dict = publication_sdgs_dict['Related_SDG']
                counts = [0] * num_of_sdgs
                for sdg, word_found_dict in sdg_dict.items():
                    sdg_match = re.search(r'\d(\d)?', sdg)
                    sdg_num = int(sdg_match.group()) if sdg_match is not None else num_of_sdgs
                    count = len(word_found_dict['Word_Found'])
                    counts[sdg_num - 1] = count
                results[doi] = counts # add DOI with array of SDG keyword counts to results.

            return results

    # MODULE CATALOGUE MODEL
    def __read_module_sdg_model_data(self):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.ModulePrediction
        data = col.find()

        # with open('NLP/MODEL_RESULTS/training_results.json', 'rb') as json_file:
            # data = json.load(json_file)
        for i in data:
            docTopics = i['Document Topics']
            results = {}
            counter = 0
            for module in docTopics:
                weights_tuples = docTopics[module]
                weights = [0] * num_of_sdgs
                for i in range(len(weights_tuples)):
                    weights_tuples[i] = weights_tuples[i].replace('(', '').replace(')', '').replace('%', '').replace(' ', '').split(',')
                    try:
                        w = float(weights_tuples[i][1])
                    except:
                        w = 0.0
                    weights[i] = w
                    results[module] = weights
            client.close()
            return results

    # MODULE CATALOGUE COUNT
    def __read_module_sdg_count_data(self):
        with open('MODULE_CATALOGUE/matchedModulesSDG.json', 'rb') as json_file:
            data = json.load(json_file)
            results = {} # dictionary with module_code and SDG keyword counts.
            for module, module_name_sdgs_dict in data.items():
                sdg_dict = module_name_sdgs_dict['Related_SDG']
                counts = [0] * num_of_sdgs
                for sdg, word_found_dict in sdg_dict.items():
                    sdg_match = re.search(r'\d(\d)?', sdg)
                    sdg_num = int(sdg_match.group()) if sdg_match is not None else num_of_sdgs
                    count = len(word_found_dict['Word_Found'])
                    counts[sdg_num - 1] = count
                results[module] = counts # add module_code with array of SDG keyword counts to results.

            return results

    def __compute_similarity(self, vec_A, vec_B):
        dot = vec_A.dot(vec_B)
        vec_A_magnitude = np.sqrt(vec_A.dot(vec_A))
        vec_B_magnitude = np.sqrt(vec_B.dot(vec_B))
        return dot / (vec_A_magnitude * vec_B_magnitude) # cosine of the angle between vec_A and vec_B.

    def __validate(self, read_count, read_model):
        model_data = read_model()
        count_data = read_count()
        e = 0.01 # small offset value added to counts which are zero.

        results = {}

        for key, weights in model_data.items():
            vec_A = np.array(weights) * 1.0 / 100 # probability predicted by model determines how much a document is related to each SDG.

            original_counts = count_data[key]
            counts = original_counts.copy()
            for i in range(num_of_sdgs):
                if counts[i] == 0:
                    counts[i] = e
            counts_sum_inv = 1.0 / sum(counts)
            vec_B = np.array(counts) * counts_sum_inv # probability predicted by counting SDG occurances.

            sim = self.__compute_similarity(vec_A, vec_B)

            # Populate dictionary of with ModuleID, Similarity and SDG keyword counts.
            validation_dict = {}
            validation_dict["Similarity"] = sim
            validation_dict["SDG_Keyword_Counts"] = original_counts
            results[key] = validation_dict

        # Sort dictionary by Similarity.
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['Similarity']))
        return sorted_results

    def __writeToDBP_Modules(self, data):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.ModuleValidation
        key = value = data
        col.update(key, value, upsert=True)

    def __writeToDBP_Scopus(self, data):
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.Scopus
        col = db.ScopusValidation
        key = value = data
        col.update(key, value, upsert=True)
    
    def run(self):
        module_results = self.__validate(self.__read_module_sdg_count_data, self.__read_module_sdg_model_data)
        scopus_results = self.__validate(self.__read_scopus_sdg_count_data, self.__read_scopus_sdg_model_data)

        with open('MODULE_CATALOGUE/moduleValidationSDG.json', 'w') as outfile:
            json.dump(module_results, outfile)
        with open('SCOPUS/scopusValidationSDG.json', 'w') as outfile:
            json.dump(scopus_results, outfile)
        self.__writeToDBP_Modules(module_results)
        self.__writeToDBP_Scopus(scopus_results)
        print("FINISHED: Module & Scopus Validations")
