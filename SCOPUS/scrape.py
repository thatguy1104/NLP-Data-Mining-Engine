import glob, os, sys
import pybliometrics.scopus as ok
import pandas as pd
import json
import csv
import math
import numpy as np


class Scopus():
    def __init__(self):
        self.__rps_data_file = "SCOPUS/GIVEN_DATA_FILES/cleaned_RPS_export_2015.csv"
        self.__f = open("SCOPUS/log.txt", "w")

    def __progress(self, count, total, custom_text, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' %(bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def __getDOIs(self, columns, limit=None):
        if not limit:
            return pd.read_csv(self.__rps_data_file)[columns]
        return pd.read_csv(self.__rps_data_file)[columns].head(limit)

    def getInfo(self, scopusID):
        valid = True
        try:
            scopus = ok.AbstractRetrieval(scopusID, view='FULL')
        except:
            self.__f.write("Invalid DOI: " + scopusID + "\n")
            
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

    def formatData(self, data):
        authorData = {}
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

    def cleanerFileReadings(self, limit):
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

        return result

    def deleteAllFiles(self):
        files = glob.glob('SCOPUS/GENERATED_FILES/*')
        for f in files:
            os.remove(f)

    def createAllFiles(self):
        data = self.__cleanerFileReadings(limit=3000)
        
        l = len(data)
        counter = 1

        for i in data:
            data_dict = self.__getInfo(i)
            if data_dict != "invalid":
                self.__progress(counter, l, "writing files")
                self.__f.write("Written " + str(counter) + "/" + str(l) + " files " + "DOI: " + i + "\n")
                reformatted_data = self.formatData(data_dict)
                with open("SCOPUS/GENERATED_FILES/" + str(counter) + '.json', 'w') as outfile:
                    json.dump(reformatted_data, outfile)
                counter += 1

        self.__f.write("\nDONE")
        self.__f.close()
