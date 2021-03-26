import pyodbc

class Create_ModuleData():
    def __init__(self):
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'

    def create(self):
        """
            Instantiates MySQL Database Table <ModuleData>
        """

        myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        cur = myConnection.cursor()

        create = """CREATE TABLE ModuleData(
                        Department_Name      VARCHAR(150),
                        Department_ID        VARCHAR(150),
                        Module_Name          VARCHAR(150),
                        Module_ID            VARCHAR(150) PRIMARY KEY,
                        Faculty              VARCHAR(100),
                        Credit_Value         FLOAT,
                        Module_Lead          VARCHAR(100),
                        Catalogue_Link       VARCHAR(MAX),
                        Description          VARCHAR(MAX),
                        Last_Updated         DATETIME DEFAULT CURRENT_TIMESTAMP
                    );"""

        cur.execute(create)
        myConnection.commit()
        myConnection.close()
