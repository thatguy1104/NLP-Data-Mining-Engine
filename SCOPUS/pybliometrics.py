import pybliometrics.scopus as ok
import json
import csv

def getInfo(scopusID):
    scopus = ok.AbstractRetrieval(scopusID, view='FULL')
    
    authors = scopus.authors
    author_group = scopus.authorgroup
    title = scopus.title
    date = int(scopus.coverDate[:4])
    source = scopus.srctype
    volume = scopus.volume
    issue = int(scopus.issueIdentifier)
    # artNo = 
    pageStart = int(scopus.startingPage)
    pageEnd = int(scopus.endingPage)
    citedBy = scopus.citedby_count
    doi = scopus.doi
    link = scopus.scopus_link
    affiliations = scopus.affiliation
    abstract = scopus.abstract
    authorKeywords = scopus.authkeywords
    indexKeywords = scopus.idxterms
    docType = scopus.aggregationType
    # publicationStage = 
    openAccess = int(scopus.openaccess)
    source = scopus.sourcetitle_abbreviation
    eid = scopus.eid

    # Additional data
    subjectAreas = scopus.subject_areas

    return {"Authors": authors, "AuthorGroup": author_group, "Title": title, "Year": date, "Source": source,
            "Volume" : volume, "Issue" : issue, "Art.No" : None, "PageStart" : pageStart,
            "PageEnd" : pageEnd, "CitedBy" : citedBy, "DOI" : doi, "Link" : link,
            "Addiliations" : affiliations, "Abstract" : abstract, "AuthorKeywords" : authorKeywords,
            "IndexKeywords" : indexKeywords, "DocumentType" : docType, "PublicationStage" : None,
            "OpenAccess" : openAccess, "Source" : source, "EID" : eid, "SubjectAreas" : subjectAreas}

def formatData(data):
    authorData = {}
    for i in data['AuthorGroup']:
        affiliationID = i[0]
        affiliationName = i[2]
        authorID = i[7]
        authorName = i[8]
        print(authorName, authorID, affiliationID, affiliationName)
        author = {"Name" : authorName, "AuthorID" : authorID, "AffiliationID" : affiliationID, "AffiliationName" : affiliationName}
        authorData[authorID] = author
    del data['Authors']
    del data['AuthorGroup']
    del data['Addiliations']
    data['AuthorData'] = authorData
    return data

def writeToDB():
    with open('final_data.json') as json_file:
        data = json.load(json_file)
    

# data_dict = getInfo('2-s2.0-85095962680')
# reformatted_data =formatData(data_dict)
writeToDB()

