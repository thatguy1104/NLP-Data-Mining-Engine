import numpy as np
import pandas as pd
import json
import re

matchedModulesSDG_filepath = "MODULE_CATALOGUE/matchedModulesSDG.json"
matchedPublicationsSDG_filepath = "SCOPUS/matchedScopusSDG.json"
num_of_sdgs = 18


class ValidateLDA():

    def __read_module_sdg_training_data(self):
        with open('NLP/MODEL_RESULTS/training_results.json') as json_file:
            data = json.load(json_file)
            docTopics = data['Document Topics']
            results = {}
            counter = 0
            for module in docTopics:
                weights_tuples = docTopics[module]
                weights = [0] * num_of_sdgs
                for i in range(len(weights_tuples)):
                    weights_tuples[i] = weights_tuples[i].replace('(', '').replace(')', '').replace('%', '').replace(' ', '').split(',')
                    sdgNum = int(weights_tuples[i][0])
                    weightSDG = weights_tuples[i][1]
                    try:
                        weightSDG = float(weightSDG)
                    except:
                        weightSDG = 0.0
                    weights[sdgNum - 1] = weightSDG
                    results[module] = weights

            return results

    def __read_module_sdg_count_data(self):
        with open('MODULE_CATALOGUE/matchedModulesSDG.json', 'r') as json_file:
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

                # Add module code with array of SDG keyword counts to dictionary.
                results[module] = counts

            return results

    def __cosine_similarity(self, vec_A, vec_B):
        dot = vec_A.dot(vec_B)
        vec_A_magnitude = np.sqrt(vec_A.dot(vec_A))
        vec_B_magnitude = np.sqrt(vec_B.dot(vec_B))
        return dot / (vec_A_magnitude * vec_B_magnitude) # cosine of the angle between vec_A and vec_B.

    def __squashing_function(self, vec_A, vec_B):
        return 1

    def __compute_similarity(self, vec_A, vec_B):
        return self.__cosine_similarity(vec_A, vec_B) * self.__squashing_function(vec_A, vec_B)

    def __validate(self):
        count_data = self.__read_module_sdg_count_data()
        training_data = self.__read_module_sdg_training_data()
        e = 0.01 # small offset value added to counts which are zero.

        results = {}

        for module, weights in training_data.items():
            vec_A = np.array(weights) * 1.0 / 100 # probability predicted by model determines how much a document is related to each SDG.

            original_counts = count_data[module]
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
            results[module] = validation_dict

            # Sort dictionary by Similarity.
            sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['Similarity']))

        return sorted_results

    def run(self):
        results = self.__validate()
        with open('MODULE_CATALOGUE/moduleValidationSDG.json', 'w') as outfile:
            json.dump(results, outfile)
