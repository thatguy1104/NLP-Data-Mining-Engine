from MANAGERS.loader_manager import LOADER_SECTION
from MANAGERS.module_manager import MODULE_SECTION
from MANAGERS.scopus_manager import SCOPUS_SECTION
from MANAGERS.nlp_manager import NLP_SECTION

def loader_manager(modules, publications):
    loader_actions = LOADER_SECTION()
    if modules:
        loader_actions.load_modules()
    if publications:
        loader_actions.load_publications()

def module_manager(initialise, resetDB, scrape, updateStudentCount):
    module_actions = MODULE_SECTION()
    if initialise:
        module_actions.initialise()
    if resetDB:
        module_actions.resetDB_Table()
    if scrape:
        module_actions.scrapeAllModules()
    if updateStudentCount:
        module_actions.update_studentsPerModule()

def scopus_manager(scrape):
    scopus_actions = SCOPUS_SECTION()

    if scrape:
        scopus_actions.scrapeAllPublications()

def nlp_manager(run_LDA_SDG, run_LDA_IHE, run_GUIDED_LDA_SDG, run_GUIDED_LDA_IHE, module_string_match, scopus_string_match, predict_scopus_data, 
                create_SVM_dataset, run_SVM_SDG, validate_model):
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
        nlp_actions.create_SVM_dataset()
    if run_SVM_SDG:
        nlp_actions.run_SVM_SDG()    
    if validate_model:
        nlp_actions.validate_LDA()

def main():
    loader_manager(modules=False, publications=False)
    module_manager(initialise=False, resetDB=False, scrape=False, updateStudentCount=False)
    scopus_manager(scrape=False) 
    nlp_manager(run_LDA_SDG=True, run_LDA_IHE=True, run_GUIDED_LDA_SDG=False, run_GUIDED_LDA_IHE=False, module_string_match=False,
                scopus_string_match=False, predict_scopus_data=False, create_SVM_dataset=False, run_SVM_SDG=False, validate_model=False)


"""
    TESTING NOTES:
        run_LDA_SDG         --> works
        run_GUIDED_LDA_SDG  --> to be fixed (guidedlda library issues)
        module_string_match --> works
        scopus_string_match --> works
        predict_scopus_data --> works
        create_SVM_dataset  --> to be tested
        run_SVM_SDG         --> to be tested
        validate_model      --> to be tested
"""

if __name__ == "__main__":
    main()
