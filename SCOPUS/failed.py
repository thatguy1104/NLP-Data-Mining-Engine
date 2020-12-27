link = "http://zhiyzuo.github.io/python-scopus/"
link_2 = "https://github.com/pybliometrics-dev/pybliometrics"

key = "325461529e8434763946ce3efc38b9f1"

scopus = Scopus(key)
author_result_df = scopus.search_author(
    "AUTHLASTNAME(Zhao) and AUTHFIRST(Kang) and AFFIL(Iowa)")
print(author_result_df)
