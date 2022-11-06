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
            cls.dbHelper.connect(os.path.join(
                DATASET_PATH, EUROPEAN_SOCCER_DATABASE))
        return cls.dbHelper


class DataHelper(object):
    def __init__(self, data):
        self.data = data

    def getNameById(self, id):
        return self.data.loc[self.data.id == id].name.values[0]


class CountryDataHelper(DataHelper):
    pass


class LeagueDataHelper(DataHelper):
    pass


class MatchDataHelper(DataHelper):
    pass


class TeamDataHelper(DataHelper):
    def getLongTeamNameByApiId(self, id):
        return self.data.loc[self.data.team_api_id == id].team_long_name.values[0]


class MatchResultPredictDataAggregator(object):
    def __init__(self, database):
        self.database = database
        self.aggregatedData = None
        self.matchData = self.database.runQuery("SELECT * FROM Match;")
        self.countryData = self.database.runQuery("SELECT * FROM Country;")
        self.leagueData = self.database.runQuery("SELECT * FROM League;")
        self.teamData = self.database.runQuery("SELECT * FROM Team;")
        self.playerData = self.database.runQuery("SELECT * FROM Player;")
        self.countryDataHelper = CountryDataHelper(self.countryData)
        self.leagueDataHelper = LeagueDataHelper(self.leagueData)
        self.teamDataHelper = TeamDataHelper(self.teamData)

    def addCountryNameToMatches(self):
        for match in range(len(self.matchData)):
            self.matchData.loc[match, "country_name"] = self.countryDataHelper.getNameById(
                self.matchData.country_id.iloc[match]
            )

    def addLeagueNameToMatches(self):
        for match in range(len(self.matchData)):
            self.matchData.loc[match, "league_name"] = self.leagueDataHelper.getNameById(
                self.matchData.country_id.iloc[match]
            )

    def addTeamNameToMatches(self, teamType):
        for match in range(len(self.matchData)):
            self.matchData.loc[match, "{}_team_name".format(teamType)] = self.teamDataHelper.getLongTeamNameByApiId(
                self.matchData["{}_team_api_id".format(teamType)].iloc[match]
            )

    def aggregate(self):
        self.addCountryNameToMatches()
        self.addLeagueNameToMatches()
        self.addTeamNameToMatches("home")
        self.addTeamNameToMatches("away")

        # print("Aditya")
        # print("Khursale")

if __name__ == "__main__":
    print("Starting...")
    dataAggregator = MatchResultPredictDataAggregator(EuropeanSoccerDatabase())
    dataAggregator.aggregate()
