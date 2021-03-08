import os, sys, re
import json
import pandas as pd
from NLP.LDA.LDA_map import preprocess_keywords, preprocess_keyword
from NLP.preprocess import module_catalogue_tokenizer

class ScopusMap():
    def progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def load_publications(self):
        files_directory = "SCOPUS/GENERATED_FILES/"
        resulting_data = {}
        all_file_names = os.listdir(files_directory)
        for file_name in all_file_names:
            with open(files_directory + file_name) as json_file:
                data = json.load(json_file)
                if not data:
                    continue
                abstract = data["Abstract"]
                doi = data["DOI"]
                if abstract and doi:
                    title = data["Title"]

                    author_keywords = data["AuthorKeywords"]
                    if not author_keywords:
                        author_keywords = None
                    index_keywords = data["IndexKeywords"]
                    if not index_keywords:
                        index_keywords = None

                    resulting_data[doi] = {"Title" : title, "DOI" : doi, "Abstract" : abstract, "AuthorKeywords" : author_keywords, 
                            "IndexKeywords" : index_keywords}

        return resulting_data

    def read_keywords(self, data):
        resulting_data = {}
        counter = 0
        keywords = preprocess_keywords("MODULE_CATALOGUE/SDG_KEYWORDS/SDG_Keywords.csv")
        num_publications = len(data)
        num_keywords = len(keywords)

        for i in data:
            self.progress(counter, num_publications, "processing SCOPUS/matchedScopusSDG.json")
            counter += 1
            
            title = " ".join(module_catalogue_tokenizer(data[i]["Title"])) # preprocess title.
            abstract = " ".join(module_catalogue_tokenizer(data[i]["Abstract"])) # preprocess abstract.
            publication_text = title + " " + abstract

            author_keywords = data[i]["AuthorKeywords"]
            if author_keywords:
                for w in author_keywords:
                    publication_text += " " + " ".join(module_catalogue_tokenizer(w))
            index_keywords = data[i]["IndexKeywords"]
            if index_keywords:
                for w in index_keywords:
                    publication_text += " " + " ".join(module_catalogue_tokenizer(w))

            sdg_occurences = {}
            for n in range(num_keywords):
                sdg_num = n + 1
                sdg = "SDG " + str(sdg_num) if sdg_num < num_keywords else "Misc"
                sdg_occurences[sdg] = {"Word_Found": []}
                for keyword in keywords[n]:
                    if keyword in publication_text:
                        sdg_occurences[sdg]["Word_Found"].append(keyword)
                if len(sdg_occurences[sdg]["Word_Found"]) == 0:
                    del sdg_occurences[sdg]
                resulting_data[data[i]["DOI"]] = {"PublicationInfo" : data[i], "Related_SDG" : sdg_occurences}

        print()
        with open('SCOPUS/matchedScopusSDG.json', 'w') as outfile:
            json.dump(resulting_data, outfile)
        
    def run(self):
        data = self.load_publications()
        self.read_keywords(data)