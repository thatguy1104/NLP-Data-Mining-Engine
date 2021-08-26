"""
    Standalone file to analyse the results produced after running predict_publication.py on the IHE_LDA results and output the publications under each IHE speciality
"""


import json
import pandas as pd

THRESHOLD = 20


def generate_csv(data: dict, cols: list, file_name: str) -> None:
    """
        Generates the CSV file
        Processes longest column, fills others to the same length with empty string values
    """

    longest = 0
    for i in cols:
        if len(data[i]) > longest:
            longest = len(data[i])

    len_cols = []
    for i in cols:
        len_cols.append(str(i) + " (" + str(len(data[i])) + ")")

    for i in cols:
        while len(data[i]) < longest:
            data[i].append("")

    new_data = {}
    count = 0
    for i in len_cols:
        new_data[i] = data[str(count)]
        count += 1

    df = pd.DataFrame(data=new_data, columns=len_cols)
    print(df)

    df.to_csv(file_name, encoding='utf-8', index=False)


def main() -> None:
    """
        Gets the initial data for processing before output
    """

    with open('main/NLP/LDA/IHE_RESULTS/scopus_prediction_results.json', 'r') as f:
        results = json.load(f)

    lst = {}
    cols = []
    for i in range(20):
        lst[str(i)] = []
        cols.append(str(i))

    for i in range(20):
        for doi, vals in results.items():
            if vals[str(i)] >= THRESHOLD:
                lst[str(i)].append(doi)

    generate_csv(lst, cols, "main/NLP/LDA/IHE_RESULTS/pub_analyse_20.csv")


if __name__ == "__main__":
    main()