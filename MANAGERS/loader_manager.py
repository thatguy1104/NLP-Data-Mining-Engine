from LOADERS.module_loader import ModuleLoader
from LOADERS.publication_loader import PublicationLoader

class LOADER_SECTION():
    def load_modules(self):
        """
            Load modules from SQL server and serialize.
        """
        ModuleLoader().load_pymongo_db()


    def load_publications(self):
        """
            Load publications from pymongo database and serialize.
        """
        PublicationLoader().load_pymongo_db()
