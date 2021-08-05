# UCL5 MieMie
>UCL5 MieMie is an Natural Language Processing (NLP), data mining and web scraping engine to be used across UCL through research and teaching.

<br />

## Brief Introduction
Our goal is to scrape, map and generate classifiers with the intention of generating an overview of activity taking place currently at University College London through teaching and ongoing research. 

The project goals are split into 3 sections:
* Perform keyword searches on Scopus research publications of UCL academics and researchers.
* Map UCL modules to UN SDG's (United Nations Sustainable Development Goals).
* Map UCL researchers to IHE (Institute of Healthcare Engineering) subject areas and areas of expertise.

<br />

## Solution
The solution is to design, tune and implement NLP (Natural Language Processing) and machine learning algorithms to classify text for a given set of topics, each of which is categorised using an extensive set of keywords. The classification, training results and validation are then interfaced on a Django web-application which allows for interactivity via keyword searches, visual interpretation of the data, NLP and SVM model predictions.

#### Keyword Search
Our Django web application allows for performing keyword searches across UCL modules and research publications.

#### Sustainable Development Goals 
For mapping UCL modules to UN SDG's, we first compile an extensive set of keywords for 17 SDG's, including Misc (general set of keywords for all SDG's). We then use LDA (semi-supervised Latent Dirichlet Allocation using collapsed Gibbs sampling) as a first-step to learn a much larger and more representative sdg-keyword distribution and module-sdg distribution. The module-sdg distribution results are used to extract the most related SDG's for particular modules, which are then used as labels for training a more sophisticated, supervised machine learning algorithm in the form of a Support Vector Machine (SVM).

#### Institute of Healthcare Engineering
For mapping UCL research publications to IHE areas of expertise, we use the same methodology described for our SDG mapping. Initially using the LDA algorithm to annotate publications and subsequently leveraging SVM to perform final stage classifications. The final goal is to extract researchers for each of the IHE & Digital Health specialities and perform mapping against a selection of approaches to research, forming the Bubble Chart.
<br /><br />

## Project Website
The [following website](http://www.albert-mukhametov.info/web3/) gives a greater overview of the challenges and design decisions that were made, implementation using the Python programming language and research undertaken.
<br /><br />
## Meet Our Supervisor
* Marilyn Aviles - marilyn.aviles@ucl.ac.uk
## Meet the Development Team
* Aashvin Relwani - aashvin.relwani.19@ucl.ac.uk
* Albert Mukhametov - albert.mukhametov.19@ucl.ac.uk

## Viewing the Data Interface
* [Web Application](https://miemiedjangoapp.azurewebsites.net)
* [Source Code](https://github.com/thatguy1104/MieMieDjango-Web-App.git)

<br />

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Clone the Repository
Create a folder for this project, open a Terminal / Command Prompt at that folder and run the following commmand:
```bash
$ git clone https://github.com/thatguy1104/MieMieDjango-Web-App.git
$ cd NLP-Data-Mining-Engine
```

### Create & Activate Python Virtual Environment
Creating a virtual development environment:
```bash
$ python3 -m venv venv
```

Activate the environment
```bash
$ source venv/bin/activate
```

You should see (venv) at the start of the terminal string (which ends in a $)

### Navigate to the source directory
```bash
$ cd src
```
### Prerequisites
Installation of libraries required:
```bash
$ pip3 install -r requirements.txt
```

<br />

## Running the Engine
>Note: running a command impacts files, as well as certain database contents (possibility of overwriting existing values). Chronologically coherent sequence of commands is outlined below.

### Loading the publication and module data:
```bash
$ python3 global_controller.py LOAD publications
$ python3 global_controller.py LOAD modules
```
### Train the LDA for SDGs and/or IHEs
```bash
$ python3 global_controller.py NLP run_LDA_SDG
$ python3 global_controller.py NLP run_LDA_IHE
```
### Perform string-matching for SDGs (skip if only focusing on IHEs)
```bash
$ python3 global_controller.py NLP module_string_match
$ python3 global_controller.py NLP scopus_string_match
```
### Use SDG LDA results to classify publications (skip if only focusing on IHEs)
```bash
$ python3 global_controller.py NLP predict_scopus_data
```
### Prepare pickled dataset for SVM training (for SDGs and/or IHEs)
```bash
python3 global_controller.py NLP create_SDG_SVM_dataset
python3 global_controller.py NLP create_IHE_SVM_dataset
```
### Train the SVM for SDGs and/or IHEs
```bash
$ python3 global_controller.py NLP run_SVM_SDG
$ python3 global_controller.py NLP run_SVM_IHE
```
### Validate SVM SDG results against string-match ((skip if only focusing on IHEs)
```bash
$ $ python3 global_controller.py NLP validate_sdg_svm
```
### Once publication and module data are scraped, synchronise MongoDB with PostgreSQL
```bash
$ python3 global_controller.py SYNC synchronize_raw_mongodb
```
### After LDA & SVM training, synchronise results with PostgreSQL
```bash
$ python3 global_controller.py SYNC synchronize_mongodb
```
### After LDA & SVM training, use publication classification to update user data + bubble chart data
```bash
$ python3 global_controller.py SYNC synchronize_bubble
```

<br />

## Scrape Publications
Prior to scraping, firstly ensure the file titled “cleaned_RPS_export_2015.csv” in directory src/main/SCOPUS/GIVEN_DATA_FILES is up-to-date. The file should contain a column titled “DOI”. The scraper examines given DOIs, compares them to existing records and scrapes only those not already present in the database. It is vital for the file to retain its structural integrity to avoid any unexpected script errors. Secondly, setup [Scopus API key](https://dev.elsevier.com/documentation/AbstractRetrievalAPI.wadl). Once the key has been set up, ensure that you are on a UCL network (either using UCL WI-FI or connected to a UCL virtual machine). It can also be achieved via UCL VPN ([instructions](https://www.ucl.ac.uk/isd/services/get-connected/ucl-virtual-private-network-vpn)). Finally, run the following command to initiate scraping:
```
python3 global_controller.py SCRAPE_PUB
```

<br />

## Scrape Modules
Register UCL API [here](https://uclapi.com) and initialise departmental data, which is necessary to perform prior to scraping. It can be done by running the command below:
```
python3 global_controller.py MOD initialise
```
Reset current module data records
```
python3 global_controller.py MOD resetDB
```
Lastly, to reflect the current student population data, keep the file “studentsPerModule.csv” up-to-date in directory src/main/MODULE_CATALOGUE/STUDENTS_PER_MOD. To synchronise that data with the database run the following command:
```
python3 global_controller.py MOD updateStudentCount
```
Finally, module scraping can be performed. Ensure the MySQL credentials are valid and up-to-date in config.ini file (under SQL_SERVER section) and run the following command to freshly scrape the UCL module catalogue data:
```
python3 global_controller.py MOD scrape
```

<br />

## Running Tests
Ensure you are in the global project directory and run the following command to execute all unit tests:
```
python3 -m unittest discover src/test -p 'test_*.py'
```

<br />

## Data Sources Scraped
* [UCL API](https://uclapi.com/docs/) - UCL Department details
* [Scopus API](https://dev.elsevier.com/api_docs.html) - Source for UCL publication data
* [UCL Module Catalogue](https://www.ucl.ac.uk/module-catalogue) - Source for UCL module data

<br />

## NLP & Machine Learning Algorithms Used
* [Latent Dirichlet Allocation (LDA)](https://jmlr.org/papers/volume3/blei03a/blei03a.pdf) - unsupervised topic modelling algorithm used to classify text in a document to a topic
* [GuidedLDA](https://guidedlda.readthedocs.io/en/latest/) - implements latent Dirichlet allocation (LDA) using collapsed Gibbs sampling
* [Support Vector Machine (SVM)](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html) -  SVM linear classifier with SGD (Stochastic Gradient Descent) training

<br />

## Versioning
For the versions available, see the [tags on this repository](https://github.com/UCLComputerScienceCOMP0016_2020_21_Team16/tags). 

<br />

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details