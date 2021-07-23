import pandas as pd
import json
import psycopg2
import sys
from typing import Tuple
from main.CONFIG_READER.read import get_details


postgre_database = get_details("POSTGRESQL", "database")
postgre_user = get_details("POSTGRESQL", "username")
postgre_host = get_details("POSTGRESQL", "host")
postgre_password = get_details("POSTGRESQL", "password")
postgre_port = get_details("POSTGRESQL", "port")

def get_args() -> Tuple[int, bool, bool]:
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        sys.exit("Error: Wrong number of arguments")

    num_publications = sys.argv[1]
    ucl_only = False if sys.argv[2] == '0' else True
    if len(sys.argv) == 4: approach = sys.argv[3]
    else: approach = 0

    return num_publications, ucl_only, approach

def get_results(file_name: str) -> dict:
    with open(file_name) as json_file:
        results = json.load(json_file)
    return results

def query_postgres(num_publications: int):
    con = psycopg2.connect(database=postgre_database, user=postgre_user,
                               host=postgre_host, password=postgre_password, port=postgre_port)
    cur = con.cursor()

    if num_publications == '0': cur.execute("SELECT data, \"assignedSDG\" FROM public.app_publication")
    else: cur.execute("SELECT data, \"assignedSDG\" FROM public.app_publication LIMIT " + str(num_publications))
    query_result = cur.fetchall()

    cur.execute("SELECT name FROM public.app_specialtyact")
    cols = cur.fetchall()
    cols = [i[0] for i in cols]

    con.close()
    return query_result, cols

def get_authors(query_result: list, results: dict, approach: int, cols: list, ucl_only: bool) -> dict:
    THRESHOLD = 30
    data = {}
    classified_count = 0
    already_classified = False
    for i in cols:
        data[i]=[]

    for items in query_result:
        if items[0]['DOI'] in results['Document Topics']:
            assigned_IHE = results['Document Topics'][items[0]['DOI']]
            author_data = items[0]['AuthorData']

            ihe_string = items[1]['IHE_Approach_String'] if 'IHE_Approach_String' in items[1] else None
            approach = str(approach)
            if (approach != '0') and (not (ihe_string and (approach in ihe_string))):
                continue
            already_classified = False
            for i, val in enumerate(assigned_IHE):
                temp = float(val[4:-2])
                if temp >= THRESHOLD:
                    if not already_classified:
                        classified_count += 1
                        already_classified = True
                    for author_id, values in author_data.items():
                        if ucl_only:
                            if '60022148' not in values['AffiliationID']:
                                continue
                        name = ""
                        if values['Name']:
                            name = values['Name']
                        cell_data = name + " (" + author_id + ")"
                        if cell_data not in data[cols[i]]:
                            data[cols[i]].append(cell_data)

    return data

def generate_csv(data: dict, cols: list, file_name: str) -> None:
    longest = 0
    for i in cols:
        if len(data[i]) > longest:
            longest = len(data[i])

    for i in cols:
        while len(data[i]) < longest:
            data[i].append("")

    df = pd.DataFrame(data)
    print(df)

    df.to_csv(file_name, encoding='utf-8', index=False)

def main() -> None:
    input_file = "src/main/NLP/LDA/IHE_RESULTS/training_results_regmed_tisseng.json"
    output_file = "IHE_Case_Study_regmed_tisseng_RENAL.csv"
    num_publications, ucl_only, approach = get_args()
    results = get_results(input_file)

    print("Querying data")
    query_result, cols = query_postgres(num_publications)
    print("Performing analysis")
    data = get_authors(query_result, results, approach, cols, ucl_only)
    print("Saving data")
    generate_csv(data, cols, output_file)

if __name__ == "__main__":
    main()


# if len(sys.argv) < 3 or len(sys.argv) > 4:
#     sys.exit("Error: Wrong number of arguments")

# num_publications = sys.argv[1]
# ucl_only = False if sys.argv[2] == 0 else True
# if len(sys.argv) == 4: approach = sys.argv[3]
# else: approach = 0

# with open('main/NLP/LDA/IHE_RESULTS/training_results.json') as json_file:
#     results = json.load(json_file)

# con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
# cur = con.cursor()

# cur.execute("SELECT data, \"assignedSDG\" FROM public.app_publication")
# query_result = cur.fetchall()

# cur.execute("SELECT name FROM public.app_specialtyact")
# cols = cur.fetchall()
# cols = [i[0] for i in cols]

# con.close()

# threshold = 30
# data = {}
# for i in cols:
#     data[i]=[]

# for items in query_result:
#     if items[0]['DOI'] in results['Document Topics']:
#         assigned_IHE = results['Document Topics'][items[0]['DOI']]
#         author_data = items[0]['AuthorData']

#         ihe_string = items[1]['IHE_Approach_String'] if 'IHE_Approach_String' in items[1] else None
#         approach = str(approach)
#         if (approach != 0) and (not (ihe_string and approach in ihe_string)):
#             continue
#         for i, val in enumerate(assigned_IHE):
#             temp = float(val[4:-2])
#             if temp >= threshold:
#                 for author_id, values in author_data.items():
#                     name = ""
#                     if values['Name']:
#                         name = values['Name']
#                     cell_data = name + "(" + author_id + ")"
#                     if cell_data not in data[cols[i]]:
#                         data[cols[i]].append(cell_data)

# longest = 0
# for i in cols:
#     if len(data[i]) > longest:
#         longest = len(data[i])

# for i in cols:
#   while len(data[i]) < longest:
#     data[i].append("")

# df = pd.DataFrame(data)
# print(df)

# df.to_csv("IHE_Case_Study2.csv", encoding='utf-8', index=False)
