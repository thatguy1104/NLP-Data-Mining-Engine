# UCL5 MieMie
UCL5 MieMie is an Natural Language Processing (NLP), data mining and web scraping engine to be used across UCL through research and teaching.

## Brief Introduction
Our goal is to scrape, map and generate classifiers with the intention of generating an overview of activity taking place currently at University College London through teaching and ongoing research. 

The project goals are split into 3 sections:
* Perform keyword searches on Scopus research publications of UCL academics and researchers.
* Map UCL modules to UN SDGs (United Nations Sustainable Development Goals).
* Map UCL researchers to IHE (Institute of Healthcare Engineering) subject areas and areas of expertise.

## Solution
The solution is to design, tune and implement NLP (Natural Language Processing) and machine learning algorithms to classify text for a given set of topics, each of which is categorised using an extensive set of keywords. The classification, training results and validation are then interfaced on a Django web-application which allows for interactivity via keyword searches, visual interpretation of the data, NLP and SVM model predictions.

#### Keyword Search
Our Django web application allows for performing keyword searches across UCL modules and research publications.

#### Sustainable Development Goals 
For mapping UCL modules to UN SDGs, we first compile an extensive set of keywords for 17 SDGs, including Misc (general set of keywords for all SDGs). We then use GuidedLDA (semi-supervised Latent Dirichlet Allocation using collapsed Gibbs sampling) as a first-step to learn a much larger and more representative sdg-keyword distribution and module-sdg distribution. The module-sdg distribution results are used to extract the most related SDGs for particular modules, which are then used as labels for training a more sophisticated, supervised machine learning algorithm in the form of a Support Vector Machine (SVM).

#### Institute of Healthcare Engineering
For mapping UCL research publications to IHE areas of expertise, we use the same methodology described for our SDG mapping. This was more of a proof of concept, with the end-goal for future development in populating a bubble chart to classify subject areas and areas of expertise as bubbles with area proportional to the number of researchers. What we did was map UCL research publications to a subset of engienering areas of expertise.

## Project Website
The [website](http://www.albert-mukhametov.info/web3/) gives a greater overview of the challenges and design decisions that were made, implementation using the Python programming language and research undertaken.

## Meet Our Clients
* Neel Desai - neel.desai.13@ucl.ac.uk
* Marilyn Aviles - marilyn.aviles@ucl.ac.uk
* Prof. Ann Blandford - ann.blandford@ucl.ac.uk
* Dr. Simon Knowles - s.knowles@ucl.ac.uk

## Meet the Development Team
* Kareem Kermad - kareem.kermad.19@ucl.ac.uk
* Albert Mukhametov - albert.mukhametov.19@ucl.ac.uk
* Varun Wignarajah - varun.wignarajah.19@ucl.ac.uk

## Viewing the Data Interface
* [Web Application](https://miemiedjangoapp.azurewebsites.net)
* [Source Code](https://github.com/thatguy1104/MieMieDjango-Web-App.git)

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Clone the Repository
Create a folder for this project, open a Terminal / Command Prompt at that folder and run the following commmand:
```
git clone https://github.com/UCLComputerScience/COMP0016_2020_21_Team16.git

cd COMP0016_2020_21_Team16
```

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

Each of the 'managers' is a call for a specific component within the engine. The following are default values that perform all major operations needed to update all the data.

```
* keywords_merger_manager
    * sdg_keywords = False
* loader_manager
    * modules = True
    * publications = True
* module_manager
    * initialise = True
    * resetDB = False
    * scrape = False
    * updateStudentCount = True
* scopus_manager
    * scrape = False
* nlp_manager
    * run_LDA_SDG = True
    * run_LDA_IHE = True
    * run_GUIDED_LDA_SDG = False -- (AVOID using, LDA produces higher accuracy results)
    * run_GUIDED_LDA_IHE = False -- (AVOID using, LDA produces higher accuracy results)
    * module_string_match = True
    * scopus_string_match = True
    * predict_scopus_data = True
    * create_SVM_dataset = True
    * run_SVM_SDG = True
    * validate_model = True
```
The managers and their respective parameters are listed in chronological order. To run a single or multiple actions, it is required to set that parameter to True


## Data Sources Scraped
* [UCL API](https://uclapi.com/docs/) - UCL Department details
* [Scopus API](https://dev.elsevier.com/api_docs.html) - Source for UCL publication data
* [UCL Module Catalogue](https://www.ucl.ac.uk/module-catalogue) - Source for UCL module data

## NLP & Machine Learning Algorithms Used
* [Latent Dirichlet Allocation (LDA)](https://jmlr.org/papers/volume3/blei03a/blei03a.pdf) - unsupervised topic modelling algorithm used to classify text in a document to a topic
* [GuidedLDA](https://guidedlda.readthedocs.io/en/latest/) - implements latent Dirichlet allocation (LDA) using collapsed Gibbs sampling
* [Support Vector Machine (SVM)](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html) -  SVM linear classifier with SGD (Stochastic Gradient Descent) training
## Versioning
For the versions available, see the [tags on this repository](https://github.com/UCLComputerScienceCOMP0016_2020_21_Team16/tags). 
## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

