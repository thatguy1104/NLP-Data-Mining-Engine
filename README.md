# UCL5 MieMie
UCL5 MieMie is an NLP and data mining web scraping engine to be used across UCL.


## Brief Introduction
Scrape, map and generate classifiers with the intention of generating an overview of the extent of activity already taking place at University College London through teaching and ongoing research.

## Project Website
The website gives a greater overview of the challenges and design decisions that were made, implementation using the Python programming language and research undertaken. http://www.albert-mukhametov.info/web3/

## Meet Our Clients
* Neel Desai - neel.desai.13@ucl.ac.uk
* Marilyn Aviles - marilyn.aviles@ucl.ac.uk
* Prof. Ann Blandford - ann.blandford@ucl.ac.uk
* Dr. Simon Knowles - s.knowles@ucl.ac.uk
## Meet the Development Team
* Albert Mukhametov - albert.mukhametov.19@ucl.ac.uk
* Kareem Kermad - varun.wignarajah.19@ucl.ac.uk
* Varun Wignarajah - kareem.kermad.19@ucl.ac.uk
## Viewing the Data Interface
Data scraped and processed with an LDA NLP model using this tool can be visualised through our engine [web application](https://miemiedjangoapp.azurewebsites.net) and its code can be viewed [here](https://github.com/thatguy1104/MieMieDjango-Web-App.git).

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Create & Activate Python Virtual Environment
Creating a virtual development environment:
```
python3 -m venv venv
```

Activate the environment
```
source venv/bin/activate
```

You should see (venv) at the start of the terminal string (which ends in a $)
### Prerequisites
Installation of libraries required:
```
pip3 install -r requirements.txt
```

## Running the Engine
Ensure that you are in the project directory and run the following command:
```
python3 global_controller.py
```

## Editing Engine Parameters - What to Run
In order to choose which actions to perform, locate and open the global_controller.py Python file in a text editor. Locate the following function:
```
def main() -> None:
```
Inside the function you will find the following 'managers':
```
* keywords_merger_manager(...)
* loader_manager(...)
* module_manager(...)
* scopus_manager(...)
* nlp_manager(...)
```

Each of the 'managers' is a call for a specific component within the engine. As parameters, each takes in a number of actions, which by default are all set to false:

```
* keywords_merger_manager
    * sdg_keywords = False
* loader_manager
    * modules = False
    * publications = False
* module_manager
    * initialise = False
    * resetDB = False
    * scrape = False
    * updateStudentCount = False
* scopus_manager
    * scrape = False
* nlp_manager
    * run_LDA_SDG = False
    * run_LDA_IHE = False
    * run_GUIDED_LDA_SDG = False
    * run_GUIDED_LDA_IHE = False
    * module_string_match = False
    * scopus_string_match = False
    * predict_scopus_data = False
    * create_SVM_dataset = False
    * run_SVM_SDG = False
    * validate_model = False)
```
The managers and their respective parameters are listed in chronological order. To run a single or multiple actions, it is required to set that parameter to True


## Data Sources Scraped
* [UCL API](https://uclapi.com/docs/) - UCL Department details
* [Scopus API](https://dev.elsevier.com/api_docs.html) - Source for UCL publication data
* [UCL Module Catalogue](https://www.ucl.ac.uk/module-catalogue) - Source for UCL module data

## NLP Algorithms Used
* [Latent Dirichlet Allocation (LDA)](https://jmlr.org/papers/volume3/blei03a/blei03a.pdf) - unsupervised topic modelling algorithm used to classify text in a document to a topic
## Versioning
For the versions available, see the [tags on this repository](https://github.com/UCLComputerScienceCOMP0016_2020_21_Team16/tags). 
## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

