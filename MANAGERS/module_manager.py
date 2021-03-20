from MODULE_CATALOGUE.scrape import UCL_Module_Catalogue
from MODULE_CATALOGUE.INITIALISER.initialise_files import Initialiser
from MODULE_CATALOGUE.STUDENTS_PER_MOD.processPush import UpdateStudentsPerModule
from MODULE_CATALOGUE.DATABASE_FILES.db_create import Create_ModuleData
from MODULE_CATALOGUE.DATABASE_FILES.db_reset import Reset_ModuleData

class MODULE_SECTION():

    def initialise(self) -> None:
        """
            Initialises all .json files in the INITIALISER directory for further scraping
        """
        Initialiser().initialiseAll()

    def update_studentsPerModule(self) -> None:
        """
            Given CSV file <studentsPerModule.csv>, update contents of the DB table <StudentsPerModule>
        """
        UpdateStudentsPerModule().update()

    def resetDB_Table(self) -> None:
        Reset_ModuleData().reset()
        Create_ModuleData().create()

    def scrapeAllModules(self) -> None:
        """
            Given all all_module_links.json file is complete in the INITIALISER directory,
            scrapes all module content for all UCL departments
            Note: requires stable internet connection. Scrapes all modules in ~2-4 hours
        """
        UCL_Module_Catalogue().run()
