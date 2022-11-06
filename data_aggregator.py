import os
import sqlite3
from abc import abstractmethod

from pandas import DataFrame
from shared.constants import DATASET_PATH, EUROPEAN_SOCCER_DATABASE
from utils.db_helper import SqliteHelper


class EuropeanSoccerDatabase(object):

    def __new__(cls):
        if not hasattr(cls, 'dbHelper'):
            cls.dbHelper = SqliteHelper()
            cls.dbHelper.connect(os.path.join(DATASET_PATH, EUROPEAN_SOCCER_DATABASE))
        return cls.dbHelper

class MatchResultPredictDataAggregator(object):
    def __init__(self, database):
        self.database = database
        self.aggregatedData = None

    def getMatchData(self):
        return self.database.runQuery("SELECT * FROM Match;")

    def collectData(self):
        matchData = self.getMatchData()
        print(matchData.columns)


if __name__ == "__main__":
    print("Starting...")
    dataAggregator = MatchResultPredictDataAggregator(EuropeanSoccerDatabase())
    dataAggregator.collectData()
