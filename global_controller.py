from MODULE_CATALOGUE.scrape import UCL_Module_Catalogue
from MODULE_CATALOGUE.INITIALISER.initialise_files import Initialiser
from MODULE_CATALOGUE.map import ModuleMap
from SCOPUS.map import ScopusMap

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

def moduleMap():
    """
        Assigns an SDG/SDGs to each module
        Produces matchedModulesSDG.json + sdgCount.json
    """
    ModuleMap().run()

def scopusMap():
    """
        Assigns an SDG/SDGs to each research publication
        Produces matchedModulesSDG.json + sdgCount.json
    """
    ScopusMap().run()


# scrapeAllModules()
#moduleMap()
scopusMap()
