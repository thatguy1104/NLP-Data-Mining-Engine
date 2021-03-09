import glob, os, sys
import pybliometrics.scopus as ok
import pandas as pd
import json
import pathlib
import csv
import math
import numpy as np
import os
import pymongo

# from App.models import Publication
f = open("SCOPUS/log.txt", "a")
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.hw8fo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.Scopus

class GetScopusData():

    def __init__(self):
        self.__rps_data_file = "SCOPUS/GIVEN_DATA_FILES/cleaned_RPS_export_2015.csv"
        self.__generated_data = "SCOPUS/GENERATED_FILES/"

    def __progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __getDOIs(self, columns, limit=None):
        if not limit:
            return pd.read_csv(self.__rps_data_file)[columns]
        return pd.read_csv(self.__rps_data_file)[columns].head(limit)

    def __getInfo(self, scopusID):
        valid = True
        try:
        	scopus = ok.AbstractRetrieval(scopusID, view='FULL')
        except Exception as e:
            # f.write("Invalid DOI: " + scopusID + "\n")
            f.write(str(e) + "--> Error occured. " + scopusID + "\n")
            
            valid = False
            return "invalid"
        
        if valid:
            authors = scopus.authors
            author_group = scopus.authorgroup
            title = scopus.title
            try:
                date = int(scopus.coverDate[:4])
            except:
                date = None
            source = scopus.srctype
            volume = scopus.volume
            try:
                issue = int(scopus.issueIdentifier)
            except:
                issue = None
            try:
                pageStart = int(scopus.startingPage)
            except:
                pageStart = None
            try:
                pageEnd = int(scopus.endingPage)
            except:
                pageEnd = None
            citedBy = scopus.citedby_count
            doi = scopus.doi
            link = scopus.scopus_link
            affiliations = scopus.affiliation
            abstract = scopus.abstract
            authorKeywords = scopus.authkeywords
            indexKeywords = scopus.idxterms
            docType = scopus.aggregationType
            try:
                openAccess = int(scopus.openaccess)
            except:
                openAccess = None
            source = scopus.sourcetitle_abbreviation
            eid = scopus.eid

            # Additional data
            subjectAreas = scopus.subject_areas

            return {"Authors": authors, "AuthorGroup": author_group, "Title": title, "Year": date, "Source": source,
                    "Volume" : volume, "Issue" : issue, "Art.No" : None, "PageStart" : pageStart,
                    "PageEnd" : pageEnd, "CitedBy" : citedBy, "DOI" : doi, "Link" : link,
                    "Affiliations" : affiliations, "Abstract" : abstract, "AuthorKeywords" : authorKeywords,
                    "IndexKeywords" : indexKeywords, "DocumentType" : docType, "PublicationStage" : None,
                    "OpenAccess" : openAccess, "Source" : source, "EID" : eid, "SubjectAreas" : subjectAreas}

    def __formatData(self, data):
        authorData = {}
        # if "AuthoGroup" in data:
        if data['AuthorGroup']:
            for i in data['AuthorGroup']:
                affiliationID = i[0]
                affiliationName = i[2]
                authorID = i[7]
                authorName = i[8]
                author = {"Name" : authorName, "AuthorID" : authorID, "AffiliationID" : affiliationID, "AffiliationName" : affiliationName}
                authorData[authorID] = author
            del data['AuthorGroup']
            del data['Authors']
            del data['Affiliations']
            data['AuthorData'] = authorData
            return data
        return None

    def __cleanerFileReadings(self, limit):
        one_researcher = self.__getDOIs(["DOI"], limit)
        doi_list = list(one_researcher["DOI"])
        doi = set(doi_list)
        result = set()

        for i in doi:
            if i is np.nan:
                continue
            if ',' in i:
                temp = i.split(',')
                for j in temp:
                    result.add(j)
            else:
                result.add(i)

        already_scraped_DOI = []   
        col = db.Data
        data = col.find()
        for i in data:
            already_scraped_DOI.append(i["DOI"])

        exists = notexists = 0
        new_doi = set()
        for elem in result:
            if elem in already_scraped_DOI:
                exists += 1
            else:
                new_doi.add(elem)
                notexists += 1
        print("Already existed", exists)
        print("New doi's", notexists)
        print()
        return new_doi

    def __renameAllFiles(self):
        for path in pathlib.Path(self.__generated_data).iterdir():
            if path.is_file():
                with open(path) as json_file:
                    data_ = json.load(json_file)
                    if data_:
                        old_name = path.stem
                        old_extension = path.suffix
                        directory = path.parent
                        new_name = data_['EID'] + old_extension
                        path.rename(pathlib.Path(directory, new_name))

    def __deleteAllFiles(self):
        files = glob.glob('SCOPUS/GENERATED_FILES/*')
        for f in files:
            os.remove(f)

    def __pushToMongoDB(self, data):
        col = db.Data
        key = value = data
        col.update(key, value, upsert=True)

    def createAllFiles(self, limit):
        data = self.__cleanerFileReadings(limit=limit)
        l = len(data)
        
        counter = 1
        for i in data:
            if counter < 1000:
                data_dict = self.__getInfo(i)
                if data_dict != "invalid":
                    self.__progress(counter, l, "scraping Scopus publications")
                    f.write("Written " + str(counter) + "/" + str(l) + " files " + "DOI: " + i + "\n")
                    reformatted_data = self.__formatData(data_dict)
                    self.__pushToMongoDB(reformatted_data)
                    # with open("SCOPUS/GENERATED_FILES/" + data_dict["EID"] + '.json', 'w') as outfile:
                    #     json.dump(reformatted_data, outfile)
                    counter += 1
        print()
        f.write("\nDONE")
        f.close()
        client.close()


