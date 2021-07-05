import pyodbc


def getSQL_connection():
    server = 'summermiemieservver.database.windows.net'
    database = 'summermiemiedb'
    username = 'miemie_login'
    password = 'e_Paswrd?!'
    driver = '{ODBC Driver 17 for SQL Server}'
    myConnection = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    return myConnection


def tableauVisualisation():
    curr = getSQL_connection().cursor()

    query = """
        SELECT ModuleData.Faculty, SUM(StudentsPerModule.NumberOfStudents), COUNT(TestModAssign.Module_ID), COUNT(DISTINCT(TestModAssign.SDG)) FROM [dbo].[StudentsPerModule]
        INNER JOIN ModuleData ON StudentsPerModule.ModuleID = ModuleData.Module_ID
        INNER JOIN TestModAssign ON StudentsPerModule.ModuleID = TestModAssign.Module_ID
        GROUP BY ModuleData.Faculty"""
    curr.execute(query)
    faculty_bubble_sdg = curr.fetchall() # (faculty name, num of students, num of modules, sdg coverage)

    query = """
        SELECT ModuleData.Department_Name, COUNT(TestModAssign.Module_ID), COUNT(DISTINCT(TestModAssign.SDG)), SUM(StudentsPerModule.NumberOfStudents) FROM [dbo].[ModuleData]
        INNER JOIN TestModAssign ON ModuleData.Module_ID = TestModAssign.Module_ID
        INNER JOIN StudentsPerModule ON ModuleData.Module_ID = StudentsPerModule.ModuleID
        GROUP BY ModuleData.Department_Name"""

    curr.execute(query)
    department_bubble_sdg = curr.fetchall() # (department name, num of modules, sdg coverage, num of students)

    for i in faculty_bubble_sdg:
        print(i)

    print()
    print()

    for i in department_bubble_sdg:
        print(i)

tableauVisualisation()
