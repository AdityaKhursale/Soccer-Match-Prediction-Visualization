import logging
import sqlite3
import traceback
from abc import abstractmethod

import pandas as pd


class DatabaseHelper(object):

    def __init__(self):
        self.connection = None

    @abstractmethod
    def connect(self, database_name):
        pass

    @abstractmethod
    def runQuery(self, query):
        pass


class SqliteHelper(DatabaseHelper):

    def connect(self, database_name):
        try:
            self.connection = sqlite3.connect(database_name)
        except Exception:
            logging.error(traceback.format_exc())
            return False
        return True

    def runQuery(self, query):
        if not self.connection:
            logging.error("Database connection is not active")
        return pd.read_sql(query, self.connection)
