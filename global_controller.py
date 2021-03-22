from MANAGERS.keywords_merger_manager import KEYWORDS_MERGER_SECTION
from MANAGERS.loader_manager import LOADER_SECTION
from MANAGERS.module_manager import MODULE_SECTION
from MANAGERS.scopus_manager import SCOPUS_SECTION
from MANAGERS.nlp_manager import NLP_SECTION

def keywords_merger_manager(sdg_keywords):
    keywords_merger_actions = KEYWORDS_MERGER_SECTION() 
    if sdg_keywords:
        keywords_merger_actions.merge_sdg_keywords()

def loader_manager(modules, publications):
    loader_actions = LOADER_SECTION()
    if modules:
        loader_actions.load_modules()
    if publications:
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

def nlp_manager(run_LDA_SDG: bool, run_LDA_IHE: bool, run_GUIDED_LDA_SDG: bool, run_GUIDED_LDA_IHE: bool,
                module_string_match: bool, scopus_string_match: bool, predict_scopus_data: bool,
                create_SVM_dataset: bool, run_SVM_SDG: bool, validate_sdg_svm: bool) -> None:
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
    if run_LDA_SDG:
        nlp_actions.run_LDA_SDG()
    if run_LDA_IHE:
        nlp_actions.run_LDA_IHE()
    if run_GUIDED_LDA_SDG:
        nlp_actions.run_GUIDED_LDA_SDG()
    if run_GUIDED_LDA_IHE:
        nlp_actions.run_GUIDED_LDA_IHE()
    if module_string_match:
        nlp_actions.module_string_match()
    if scopus_string_match:
        nlp_actions.scopus_string_match()
    if predict_scopus_data:
        nlp_actions.predictScopus()
    if create_SVM_dataset:
        nlp_actions.create_SDG_SVM_dataset(True, True)
    if run_SVM_SDG:
        nlp_actions.run_SVM_SDG()    
    if validate_sdg_svm:
        nlp_actions.validate_SDG_SVM()

def main() -> None:
    """
        Controller for loader_manager, module_manager, scopus_manager, nlp_manager
        Specify boolean (true / false) for an action to perform
    """
    
    keywords_merger_manager(sdg_keywords=False)
    loader_manager(modules=False, publications=False)
    module_manager(initialise=False, resetDB=False, scrape=False, updateStudentCount=False)
    scopus_manager(scrape=False)
    nlp_manager(run_LDA_SDG=False, run_LDA_IHE=False, run_GUIDED_LDA_SDG=False, run_GUIDED_LDA_IHE=False, module_string_match=False,
                scopus_string_match=True, predict_scopus_data=False, create_SVM_dataset=False, run_SVM_SDG=False, validate_sdg_svm=True)
    
if __name__ == "__main__":
    main()