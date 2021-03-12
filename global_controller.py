from MANAGERS.module_manager import MODULE_SECTION
from MANAGERS.scopus_manager import SCOPUS_SECTION
from MANAGERS.nlp_manager import NLP_SECTION

def module_manager(initialise, resetDB, scrape, mapToSDG, updateStudentCount):
    module_actions = MODULE_SECTION()
    if initialise:
        module_actions.initialise()
    if resetDB:
        module_actions.resetDB_Table()
    if scrape:
        module_actions.scrapeAllModules()
    if mapToSDG:
        module_actions.map_modules()
    if updateStudentCount:
        module_actions.update_studentsPerModule()

def scopus_manager(scrape, mapToSDG):
    scopus_actions = SCOPUS_SECTION()
    if scrape:
        scopus_actions.scrapeAllPublications()
    if mapToSDG:
        scopus_actions.scopusMap()

def nlp_manager(run_LDA_SDG, run_GUIDED_LDA_SDG, initialise_SVM, predict_scopus_data, create_SVM_dataset, validate_model):
    nlp_actions = NLP_SECTION()
    if run_LDA_SDG:
        nlp_actions.run_LDA_SDG()
    if run_GUIDED_LDA_SDG():
        nlp_actions.run_GUIDED_LDA_SDG()
    if initialise_SVM:
        nlp_actions.initialise_SVM_model()
    if predict_scopus_data:
        nlp_actions.predictScopus()
    if create_SVM_dataset:
        nlp_actions.create_SVM_dataset()
    if validate_model:
        nlp_actions.validate_LDA()

def main():
    module_manager(initialise=False, resetDB=False, scrape=False, mapToSDG=False, updateStudentCount=False)
    scopus_manager(scrape=False, mapToSDG=False) 
    nlp_manager(run_LDA_SDG=True, run_GUIDED_LDA_SDG=False, initialiseSVM=False, predict_scopus_data=False, create_SVM_dataset=False, validate_model=False)

if __name__ == "__main__":
    main()
