import pyodbc
from main.CONFIG_READER.read import get_details

class Reset_ModuleData():
    def __init__(self):
        self.server = get_details("SQL_SERVER", "client")
        self.database = get_details("SQL_SERVER", "database")
        self.username = get_details("SQL_SERVER", "username")
        self.password = get_details("SQL_SERVER", "password")
        self.driver = get_details("SQL_SERVER", "driver")

    def reset(self):
        """
            Deletes (if exists) MySQL Database Table <ModuleData>
        """

        myConnection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server +';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        cur = myConnection.cursor()
        cur.execute("DROP TABLE IF EXISTS ModuleData;")
        myConnection.commit()
        myConnection.close()
