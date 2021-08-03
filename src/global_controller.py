from main.MANAGERS.keywords_merger_manager import KEYWORDS_MERGER_SECTION
from main.MANAGERS.loader_manager import LOADER_SECTION
from main.MANAGERS.module_manager import MODULE_SECTION
from main.MANAGERS.scopus_manager import SCOPUS_SECTION
from main.MANAGERS.nlp_manager import NLP_SECTION
from main.MANAGERS.synchronizer_manager import SYNC_SECTION

import sys

def keywords_merger_manager(sdg_keywords: bool) -> None:
    keywords_merger_actions = KEYWORDS_MERGER_SECTION() 
    if sdg_keywords:
        keywords_merger_actions.merge_sdg_keywords()

def loader_manager(load_dictionary: dict) -> None:
    loader_actions = LOADER_SECTION()
    if load_dictionary['modules']:
        loader_actions.load_modules()
    if load_dictionary['publications']:
        loader_actions.load_publications()

def module_manager(initialise: bool, resetDB: bool, scrape: bool, updateStudentCount: bool) -> None:
    """
        Manager for MODULE_CATALOGUE
        Actions: intialise department files and catalogue links, reset database table, scrape data, update student count per module
    """

    module_actions = MODULE_SECTION()
    if initialise:
        module_actions.initialise()
    if resetDB:
        module_actions.resetDB_Table()
    if scrape:
        module_actions.scrapeAllModules()
    if updateStudentCount:
        module_actions.update_studentsPerModule()

def scopus_manager(scrape: bool) -> None:
    """
        Manager for SCOPUS
        Actions: gather data from Scopus API
    """

    scopus_actions = SCOPUS_SECTION()
    if scrape:
        scopus_actions.scrapeAllPublications()

def nlp_manager(nlp_dictionary: dict) -> None:
    """
        Manager for NLP
        Actions: 
            LDA - run it for SDG & IHE
            Guided LDa - run it for SDG & IHE
            String match - for modules & publications
            Prediction for publication data (SDG classification)
            SVM - initialise dataset, run it for SDG
            Validate Svm model against SDG string matching assignment (for modules & publicatoins)
    """

    nlp_actions = NLP_SECTION()
    if nlp_dictionary["run_LDA_SDG"]:
        nlp_actions.run_LDA_SDG()
    if nlp_dictionary["run_LDA_IHE"]:
        nlp_actions.run_LDA_IHE()
    if nlp_dictionary["module_string_match"]:
        nlp_actions.module_string_match()
    if nlp_dictionary["scopus_string_match"]:
        nlp_actions.scopus_string_match()
    if nlp_dictionary["predict_scopus_data"]:
        nlp_actions.predictScopus()
    if nlp_dictionary["create_SDG_SVM_dataset"]:
        nlp_actions.create_SDG_SVM_dataset(True, True)
    if nlp_dictionary["create_IHE_SVM_dataset"]:
        nlp_actions.create_IHE_SVM_dataset()
    if nlp_dictionary["run_SVM_SDG"]:
        nlp_actions.run_SVM_SDG()
    if nlp_dictionary["run_SVM_IHE"]:
        nlp_actions.run_SVM_IHE()
    if nlp_dictionary["validate_sdg_svm"]:
        nlp_actions.validate_SDG_SVM()
    
def sync_manager(sync_dictionary: dict) -> None:
    """
        Synchronizes raw scraped data (modules + publications) with Django's PostgreSQL
        Synchronizes processed validation & prediction (modules + publications) with Django's PostgreSQL
    """

    sync_actions = SYNC_SECTION()
    if sync_dictionary["synchronize_raw_mongodb"]:
        sync_actions.synchronize_mongo_PREMODEL()
    if sync_dictionary["synchronize_mongodb"]:
        sync_actions.synchronize_mongodb_POSTMODEL()
    if sync_dictionary["synchronize_bubble"]:
        sync_actions.synchronize_mongodb_BUBBLE()

def main(nlp_dictionary: dict, sync_dictionary: dict, load_dictionary: dict) -> None:
    """
        Controller for keyword_merger_manager loader_manager, module_manager, scopus_manager, nlp_manager
        Specify boolean (true / false) to perform specified action
    """

    keywords_merger_manager(sdg_keywords=False)
    loader_manager(modules=False, publications=False) # Needs to be done after each scrape
    module_manager(initialise=False, resetDB=False, scrape=False, updateStudentCount=False)
    scopus_manager(scrape=False)

    nlp_manager(nlp_dictionary)
    sync_manager(sync_dictionary)
    loader_manager(load_dictionary)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 3: sys.exit("Error: Too many arguments")

    nlp_dictionary = {
        "run_LDA_SDG": False,
        "run_LDA_IHE": False,
        "module_string_match": False,
        "scopus_string_match": False,
        "predict_scopus_data": False,
        "create_SDG_SVM_dataset": False,
        "create_IHE_SVM_dataset": False,
        "run_SVM_SDG": False,
        "run_SVM_IHE": False,
        "validate_sdg_svm": False,
    }
    sync_dictionary = {
        "synchronize_raw_mongodb": False,
        "synchronize_mongodb": False,
        "synchronize_bubble": False,
    }
    load_dictionary = {
        "publications": False,
        "modules": False
    }

    if args[0] == "NLP": nlp_dictionary[args[1]] = True
    elif args[0] == "SYNC": sync_dictionary[args[1]] = True
    elif args[0] == "LOAD": load_dictionary[args[1]] = True
    else: sys.exit("Error: Invalid arguments")
    main(nlp_dictionary, sync_dictionary, load_dictionary)

"""
    python3 global_controller.py NLP run_LDA_SDG
    python3 global_controller.py NLP run_LDA_IHE
    python3 global_controller.py NLP module_string_match
    python3 global_controller.py NLP scopus_string_match
    python3 global_controller.py NLP predict_scopus_data
    python3 global_controller.py NLP create_SDG_SVM_dataset
    python3 global_controller.py NLP create_IHE_SVM_dataset
    python3 global_controller.py NLP run_SVM_SDG
    python3 global_controller.py NLP run_SVM_IHE
    python3 global_controller.py NLP validate_sdg_svm
"""

"""
    python3 global_controller.py SYNC synchronize_raw_mongodb
    python3 global_controller.py SYNC synchronize_mongodb
    python3 global_controller.py SYNC synchronize_bubble

    python3 src/main/NLP/LDA/IHE_RESULTS/analyse_results.py
"""

"""
    python3 global_controller.py LOAD publications
    python3 global_controller.py LOAD modules
"""