import psycopg2
import csv
import json
from main.CONFIG_READER.read import get_details

def getPostgres():
    postgre_database = get_details("POSTGRESQL", "database")
    postgre_user = get_details("POSTGRESQL", "username")
    postgre_host = get_details("POSTGRESQL", "host")
    postgre_password = get_details("POSTGRESQL", "password")
    postgre_port = get_details("POSTGRESQL", "port")
    con = psycopg2.connect(database=postgre_database, user=postgre_user,
                           host=postgre_host, password=postgre_password, port=postgre_port)

    cur = con.cursor()
    cur.execute("""
        select 
            "title", "data", "assignedSDG"
            from "App_publication"
    """)
    result = cur.fetchall()
    return result

def write_to_csv(dataset):
    with open('src/main/NLP/SVM/SDG_RESULTS/svm_sdg_assignments.csv', mode='w') as svm_sdg_assignments:
        employee_writer = csv.writer(svm_sdg_assignments, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(["DOI", "Title", "SDG"])
        for data in dataset:
            doi = data[0]
            assignment = data[1]
            employee_writer.writerow([data[0], data[1], data[2]])

def process():
    data = getPostgres()
    l = len(data)
    result = []
    counter = 1
    for pub in data:
        print("Processing", counter, "/", str(l))
        sdg_assignments = pub[2]
        title = pub[0]
        doi = pub[1]['DOI']
        if sdg_assignments:
            if sdg_assignments['SVM_Prediction']:
                result.append([doi, title, sdg_assignments['SVM_Prediction']])
        counter += 1
    
    write_to_csv(result)
        

        


if __name__ == "__main__":
    process()
