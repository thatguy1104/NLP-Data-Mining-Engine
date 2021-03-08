from MODULE_CATALOGUE.scrape import UCL_Module_Catalogue
from MODULE_CATALOGUE.INITIALISER.initialise_files import Initialiser
from MODULE_CATALOGUE.STUDENTS_PER_MOD.processPush import UpdateStudentsPerModule
from MODULE_CATALOGUE.DATABASE_FILES.db_create import Create_ModuleData
from MODULE_CATALOGUE.DATABASE_FILES.db_reset import Reset_ModuleData
from MODULE_CATALOGUE.map import ModuleMap
from SCOPUS.map import ScopusMap
from SCOPUS import renameGeneratedFiles
from SCOPUS.scrape import Scopus
from NLP.validate import ValidateLDA

class MODULE_SECTION():

    def initialise(self):
        """
            Initialises all .json files in the INITIALISER directory for further scraping
        """
        Initialiser().initialiseAll()

    def update_studentsPerModule(self):
        """
            Given CSV file <studentsPerModule.csv>, update contents of the DB table <StudentsPerModule>
        """
        UpdateStudentsPerModule().update()

    def resetDB_Table(self):
        Reset_ModuleData().reset()
        Create_ModuleData().create()

    def scrapeAllModules(self):
        """
            Given all all_module_links.json file is complete in the INITIALISER directory,
            scrapes all module content for all UCL departments
            Note: requires stable internet connection. Scrapes all modules in ~2-4 hours
        """
        UCL_Module_Catalogue().run()

    def map_modules(self):
        """
            Assigns an SDG/SDGs to each module
            Produces matchedModulesSDG.json
        """
        ModuleMap().run()

class SCOPUS_SECTION():

    def renameGeneratedFiles(self):
        """
            In case of error in writing files to SCOPUS/GENERATED_FILES, this script corrects file names for consistency and integrity
        """
        renameGeneratedFiles.rename()

    def scrapeAllPublications(self):
        """
            Populate directory: SCOPUS/GENERATED_FILES/ with JSON files, each containined data on a research publication
            Used in Django web application and NLP model training + validation
            Note 1: Requires API key (10,000 weekly quota)
            Note 2: Stable internet connection
            Note 3: Scrapes quota limit in ~6-8 hours
            Note 4: Scraping machine must be either on UCL network or utilises UCL Virtual Private Network (otherwise, Scopus API throws affiliation authorisation error)
        """
        Scopus.createAllFiles()

    def scopusMap(self):
        """
            Assigns an SDG/SDGs to each research publication
            Produces matchedScopusSDG.json
        """
        ScopusMap().run()

class NLP_SECTION():

    def merge_SDG_keywords(self):
        pass

    def validate(self):
        ValidateLDA().run()



def manager():
    module_actions = MODULE_SECTION()
    # module_actions.initialise()
    module_actions.resetDB_Table()
    module_actions.scrapeAllModules()
    # module_actions.map_modules()

    # module_actions.update_studentsPerModule()


#module_actions = MODULE_SECTION()
#module_actions.map_modules()

# module_actions.initialise()
# module_actions.update_studentsPerModule()

scopus_actions = SCOPUS_SECTION()
scopus_actions.scopusMap()

#nlp_actions = NLP_SECTION()
#nlp_actions.validate()