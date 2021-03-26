import psycopg2
import csv
import json

def getPostgres():
    con = psycopg2.connect(database='django_db_miemie_ucl', user='miemie_admin@miemiedjangoapp',
                           host='miemiedjangoapp.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
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
