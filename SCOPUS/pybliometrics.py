import pybliometrics.scopus as ok



def getInfo(scopusID):
    scopus = ok.AbstractRetrieval(scopusID, view='FULL')
    authors = scopus.authorgroup
    title = scopus.title
    # year = 
    source = scopus.srctype
    volume = scopus.volume
    issue = scopus.issueIdentifier
    # artNo = 
    pageStart = scopus.startingPage
    pageEnd = scopus.endingPage
    citedBy = scopus.citedby_count
    doi = scopus.doi
    link = scopus.scopus_link
    affiliations = scopus.affiliation
    abstract = scopus.abstract
    authorKeywords = scopus.authkeywords
    indexKeywords = scopus.idxterms
    
    


getInfo('85079767316')
