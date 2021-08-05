import pyodbc
from main.CONFIG_READER.read import get_details

class Create_ModuleData():
    def __init__(self):
        self.server = get_details("SQL_SERVER", "client")
        self.database = get_details("SQL_SERVER", "database")
        self.username = get_details("SQL_SERVER", "username")
        self.password = get_details("SQL_SERVER", "password")
        self.driver = get_details("SQL_SERVER", "driver")

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
