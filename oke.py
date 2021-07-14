import pandas as pd
import json
import psycopg2

with open('src/main/NLP/LDA/IHE_RESULTS/training_results.json') as json_file:
    results = json.load(json_file)

con = psycopg2.connect(database='summermiemiepostgre', user='miemie_admin@summermiemie', host='summermiemie.postgres.database.azure.com', password='e_Paswrd?!', port='5432')
cur = con.cursor()

cur.execute("SELECT data FROM public.app_publication LIMIT 5000")
query_result = cur.fetchall()

cur.execute("SELECT name FROM public.app_specialtyact")
cols = cur.fetchall()
cols = [i[0] for i in cols]

threshold = 30
data = {}
for i in cols:
  data[i]=[]

for items in query_result:
    if items[0]['DOI'] in results['Document Topics']:
        assigned_IHE = results['Document Topics'][items[0]['DOI']]
        author_data = items[0]['AuthorData']
        for i, val in enumerate(assigned_IHE):
            temp = float(val[4:-2])
            if temp >= threshold:
                for author_id, values in author_data.items():
                    name = ""
                    if values['Name']:
                        name = values['Name']
                    cell_data = name + "(" + author_id + ")"
                    data[cols[i]].append(cell_data)

longest = 0
for i in cols:
    if len(data[i]) > longest:
        longest = len(data[i])

for i in cols:
  while len(data[i]) < longest:
    data[i].append("")

df = pd.DataFrame(data)
print(df)

con.close()
df.to_csv("IHE_Case_Study.csv", encoding='utf-8', index=False)