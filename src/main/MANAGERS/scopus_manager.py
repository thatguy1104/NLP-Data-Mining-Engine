from main.SCOPUS.scrape import GetScopusData

class SCOPUS_SECTION():

    def scrapeAllPublications(self) -> None:
        """
            Populate directory: SCOPUS/GENERATED_FILES/ with JSON files, each containined data on a research publication.
            Used in Django web application and NLP model training + validation.
            Note 1: Requires API key (10,000 weekly quota).
            Note 2: Stable internet connection.
            Note 3: Scrapes quota limit in ~6-8 hours.
            Note 4: Scraping machine must be either on UCL network or utilises UCL Virtual Private Network (otherwise, Scopus API throws affiliation authorisation error).
        """
        obj = GetScopusData()
        obj.createAllFiles(None)
