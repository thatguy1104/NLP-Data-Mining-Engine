import requests
import json
from bs4 import BeautifulSoup
import lxml
import pyodbc
import datetime


class RPS:
    def __init__(self):
        print("RPS")

    def checkTableExists(self, dbcon, tablename):
        dbcur = dbcon.cursor()
        dbcur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

    def push_to_DB(self):
        pass

    # TODO
    def get_data(self):
        pass

    # TODO
    def run(self):
        pass
