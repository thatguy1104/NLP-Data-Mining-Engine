import pyodbc


class Reset_ModuleData():
    def __init__(self):
        self.server = 'miemie.database.windows.net'
        self.database = 'MainDB'
        self.username = 'miemie_login'
        self.password = 'e_Paswrd?!'
        self.driver = '{ODBC Driver 17 for SQL Server}'

    def reset(self):
        """
            Deletes (if exists) MySQL Database Table <ModuleData>
        """

        myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server +';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        cur = myConnection.cursor()
        cur.execute("DROP TABLE IF EXISTS ModuleData;")
        myConnection.commit()
        myConnection.close()
