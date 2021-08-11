import psycopg2

postgre_host = "summermiemie.postgres.database.azure.com"
postgre_database = "summermiemiepostgre"
postgre_port = 5432
postgre_user = "miemie_admin@summermiemie"
postgre_password = "e_Paswrd?!"


con = psycopg2.connect(database=postgre_database, user=postgre_user,
                       host=postgre_host, password=postgre_password, port=postgre_port)
cur = con.cursor()
cur.execute('SELECT doi, "assignedSDG" FROM public.app_publication LIMIT 10000')
result = cur.fetchall()
cur.close()



for i in result:
    if "IHE_String_Speciality_Prediction" in i[1] and len(i[1]['IHE_String_Speciality_Prediction']) != 0:
        print(i[0], i[1]['IHE_String_Speciality_Prediction'])


