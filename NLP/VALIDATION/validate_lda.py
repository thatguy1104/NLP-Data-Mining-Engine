import numpy as np
import pandas as pd
import json
import re
import pymongo

from bson import json_util

from LOADERS.module_loader import ModuleLoader
from LOADERS.publication_loader import PublicationLoader
from MONGODB_PUSHERS.mongodb_pusher import MongoDbPusher

class ValidateLDA():
    """
        Performs LDA model validation for SDGs.
    """

    def __init__(self):
        """
            Initializes total number of SDGs, module loader, publication loader and MongoDB pusher.
        """
        self.num_of_sdgs = 18
        self.module_loader = ModuleLoader()
        self.publication_loader = PublicationLoader()
        self.mongodb_pusher = MongoDbPusher()

    def __publication_model_results(self):
        """
            Loads Lda model predictions for scopus publications and stores the results as a dictionary.
        """
        data = self.publication_loader.load_prediction_results()
        results = {} # dictionary with DOI and SDG weights.

        for doi in data:
            doi = json.loads(json_util.dumps(doi)) # process mongodb response to a workable dictionary format.
            del doi['_id']
            weights = [0] * num_of_sdgs
            sdg_predictions = doi
            
            for i in range(num_of_sdgs):
                sdg = str(i + 1)
                try:
                    w = float(sdg_predictions[sdg])
                except:
                    w = 0.0
                weights[i] = w
                results[doi["DOI"]] = weights # add DOI with array of SDG weights to results.

        return results

    def __publication_string_matches_results(self):
        """
            Loads string matching keyword counts for scopus publications and stores the results as a dictionary.
        """
        data = self.publication_loader.load_string_matches_results()
        results = {}  # dictionary with DOI and SDG keyword counts.

        for doi in data:
            doi = json.loads(json_util.dumps(doi)) # process mongodb response to a workable dictionary format.
            del doi['_id']
            sdg_dict = doi['Related_SDG']
            counts = [0] * num_of_sdgs

            for sdg, word_found_dict in sdg_dict.items():
                sdg_match = re.search(r'\d(\d)?', sdg)
                sdg_num = int(sdg_match.group()) if sdg_match is not None else num_of_sdgs
                count = len(word_found_dict['Word_Found'])
                counts[sdg_num - 1] = count
            
            results[i['DOI']] = counts # add DOI with array of SDG keyword counts to results.

        return results

    def __module_model_results(self):
        """
            Loads Lda model predictions for modules and stores the results as a dictionary.
        """
        data = self.module_loader.load_prediction_results()
        results = {} # dictionary with Module_ID and SDG weights.
        
        for module in data:
            module = json.loads(json_util.dumps(module)) # process mongodb response to a workable dictionary format.
            del module['_id']
            docTopics = module['Document Topics']

            for module_id in docTopics:
                weights_tuples = docTopics[module_id]
                weights = [0] * num_of_sdgs

                for i in range(len(weights_tuples)):
                    weights_tuples[i] = weights_tuples[i].replace('(', '').replace(')', '').replace('%', '').replace(' ', '').split(',')
                    try:
                        w = float(weights_tuples[i][1])
                    except:
                        w = 0.0
                    weights[i] = w
                    results[module_id] = weights # add Module_ID with array of SDG weights to results.

        return results

    def __module_string_matches_results(self):
        """
            Loads string matching keyword counts for modules and stores the results as a dictionary.
        """
        data = self.module_loader.load_string_matches_results()
        results = {}  # dictionary with Module_ID and SDG keyword counts.

        for module in data:
            module = json.loads(json_util.dumps(module)) # process mongodb response to a workable dictionary format.
            del module['_id']
            sdg_dict = module['Related_SDG']
            counts = [0] * num_of_sdgs

            for sdg, word_found_dict in sdg_dict.items():
                sdg_match = re.search(r'\d(\d)?', sdg)
                sdg_num = int(sdg_match.group()) if sdg_match is not None else num_of_sdgs
                count = len(word_found_dict['Word_Found'])
                counts[sdg_num - 1] = count
            
            results[i['Module_ID']] = counts # add Module_ID with array of SDG keyword counts to results.

        return results

    def __compute_similarity(self, vec_A, vec_B):
        """
            The cosine similarity metric is used to measure how similar a pair of vectors are.
            Mathematically, it measures the cosine of the angle between two vectors projected in a multi-dimensional space.
        """
        dot = vec_A.dot(vec_B)
        vec_A_magnitude = np.sqrt(vec_A.dot(vec_A))
        vec_B_magnitude = np.sqrt(vec_B.dot(vec_B))
        return dot / (vec_A_magnitude * vec_B_magnitude)

    def __validate(self, read_count, read_model):
        """
            Validate Lda model results with respect to string matching keyword occurances and store as a dictionary.
        """
        model_data = read_model()
        count_data = read_count()
        e = 0.01 # small offset value added to counts which are zero.
        results = {}

        for key in model_data:
            vec_A = np.array(model_data[key]) * 1.0 / 100 # probability predicted by model determines how much a document is related to each SDG.
            original_counts = count_data[key]
            counts = original_counts.copy()
            
            for i in range(num_of_sdgs):
                if counts[i] == 0:
                    counts[i] = e
            counts_sum_inv = 1.0 / sum(counts)
            vec_B = np.array(counts) * counts_sum_inv # probability predicted by counting keyword occurances for each SDG.

            # Populate validation dictionary with Module_ID, Similarity and SDG keyword counts.
            validation_dict = {}
            validation_dict["Similarity"] = self.__compute_similarity(vec_A, vec_B)
            validation_dict["SDG_Keyword_Counts"] = original_counts
            results[key] = validation_dict

        sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['Similarity'])) # sort dictionary by Similarity.
        return sorted_results

    def run(self):
        """
            Runs the Lda model validation against string matching keyword occurances for modules and scopus research publications.
        """
        module_results = self.__validate(self.__module_string_matches_results, self.__module_model_results)
        scopus_results = self.__validate(self.__publication_string_matches_results, self.__publication_model_results)

        # Serialize validation results as JSON file.
        with open('NLP/VALIDATION/SDG_RESULTS/module_validation.json', 'w') as outfile:
            json.dump(module_results, outfile)
        with open('NLP/VALIDATION/SDG_RESULTS/scopus_validation.json', 'w') as outfile:
            json.dump(scopus_results, outfile)

        # Push validation results to MongoDB.
        self.mongodb_pusher.module_validation(module_results)
        self.mongodb_pusher.scopus_validation(scopus_results)

        print("FINISHED: Module and Scopus Validation.")