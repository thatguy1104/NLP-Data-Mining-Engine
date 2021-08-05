from main.CONFIG_READER.read import get_details
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
from typing import Optional, Union

class GetScopusData():

    def __init__(self):
        self.host = get_details("MONGO_DB", "client")
        self.client = pymongo.MongoClient(self.host)
        self.db = self.client.Scopus
        self.__rps_data_file = "main/SCOPUS/GIVEN_DATA_FILES/cleaned_RPS_export_2015.csv"
        self.f = open("main/SCOPUS/log.txt", "a")

    def __progress(self, count: int, total: int, custom_text: str, suffix='') -> None:
        """
            Visualises progress for a process given a current count and a total count
        """

        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '*' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s %s %s\r' % (bar, percents, '%', custom_text, suffix))
        sys.stdout.flush()

    def getDOIs(self, columns: list, limit: int = None) -> pd.DataFrame:
        """
            Read RPS extract into a Pandas DataFrame
        """
        return pd.read_csv(self.__rps_data_file)[columns] if not limit else pd.read_csv(self.__rps_data_file)[columns].head(limit)

    def getInfo(self, scopusID: str) -> dict:
        """
            Extracts publication data from Scopus API.
            Checks for data field existence, accumulates and returns the resulting dictionary.
        """

        valid = True # validity flag
        try:
        	scopus = ok.AbstractRetrieval(scopusID, view='FULL')
        except Exception as e:
            self.f.write(str(e) + "--> Error occured. " + scopusID + "\n")
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

    def __formatData(self, data: dict) -> Union[dict, str]:
        """
            Refactor contributors field of a given publication.
            If data is valid, returns a cleaner, optimised dictionary.
        """

        authorData = {} # valid data accumulator
        if data['AuthorGroup']:
            for i in data['AuthorGroup']:
                affiliationID = i[0]
                affiliationName = i[2]
                authorID = i[7]
                authorName = i[8]
                author = {"Name" : authorName, "AuthorID" : authorID, "AffiliationID" : affiliationID, "AffiliationName" : affiliationName}
                authorData[authorID] = author
            
            # Clean up redundant fields
            del data['AuthorGroup']
            del data['Authors']
            del data['Affiliations']
            data['AuthorData'] = authorData
            return data
        return ""

    def __cleanerFileReadings(self, limit: int) -> set:
        """
            Checks existing DOI records, returns set of DOIs not yet scraped.
            Aids in optimisation by reduction of a number of API calls, preventing quota burnout.
        """

        one_researcher = self.getDOIs(["DOI"], limit)
        doi_list = list(one_researcher["DOI"])
        doi = set(doi_list)
        result = set()

        for i in doi:
            # Skip if DOI field is blank
            if i is np.nan: continue
            # If multiple DOIs are provided in a single data field
            if ',' in i:
                temp = i.split(',')
                for j in temp:
                    result.add(j)
            else:
                result.add(i)

        already_scraped_DOI = []   
        col = self.db.Data
        data = col.find()
        # Accumulate existing DOIs from MongoDB
        for i in data:
            already_scraped_DOI.append(i["DOI"])

        # Cross reference existing and current DOI list
        exists = notexists = 0
        new_doi = set()
        for elem in result:
            if elem in already_scraped_DOI:
                exists += 1
            else:
                new_doi.add(elem)
                notexists += 1

        # For monitoring purposes:
        print("Already existed", exists)
        print("New doi's\n", notexists)

        return new_doi

    def __renameAllFiles(self) -> None:
        """
            Renames all publication files from integer-based naming to EID (alternative to DOI, unique publication ID).
            To be used if and only if publications are backed-up locally.
            Do not use in production, for developemnt / extending purposes only.
        """

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

    def __deleteAllFiles(self) -> None:
        """
            Empties a directory - SCOPUS/GENERATED_FILES
            To be used if and only if publications are backed-up locally.
            Do not use in production, for developemnt / extending purposes only.
        """

        files = glob.glob('src/main/SCOPUS/GENERATED_FILES/*')
        for f in files: os.remove(f)

    def __pushToMongoDB(self, data: dict) -> None:
        """
            Update MongoDB with newly scraped publication and its data
            MongoDB: Collection - Scopus, Cluster - Data
        """
        
        if data:
            col = self.db.Data
            col.update_one({"DOI": data['DOI']}, {"$set": data}, upsert=True)
            
    def createAllFiles(self, limit: int) -> None:
        """
            Controller method for self.
            Read DOIs, check existing records, gather data from Scopus, push to MongoDB.
            Can specify a limit for reading DOIs from an RPS extract.
            Current limit for scraping - 9000 publications (API key quota = 10,000 / week)
        """

        data = self.__cleanerFileReadings(limit=limit)
        l = len(data)
        scraping_limit_API = 9000

        counter = 1
        for i in data:
            if counter < scraping_limit_API:
                data_dict = self.getInfo(i)
                if data_dict != "invalid":
                    self.__progress(counter, scraping_limit_API, "scraping Scopus publications")
                    self.f.write("Written " + str(counter) + "/" + str(l) + " files " + "DOI: " + i + "\n")
                    reformatted_data = self.__formatData(data_dict)
                    self.__pushToMongoDB(reformatted_data)
                    counter += 1
        print()
        self.f.write("\nDONE")
        self.f.close()
        self.client.close()
