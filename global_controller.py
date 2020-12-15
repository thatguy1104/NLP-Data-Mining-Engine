from MODULE_CATALOGUE.scrape import UCL_Module_Catalogue
from MODULE_CATALOGUE.INITIALISER.initialise_files import Initialiser


def initialise():
    """
        Initialises all .json files in the INITIALISER directory for further scraping
    """
    Initialiser().initialiseAll()

def scrapeAllModules():
    """
        Given all all_module_links.json file is complete in the INITIALISER directory,
        scrapes all module content for all UCL departments
    """
    UCL_Module_Catalogue().run()


scrapeAllModules()