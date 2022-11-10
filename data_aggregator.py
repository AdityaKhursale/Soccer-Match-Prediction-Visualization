import copy
import os
import sqlite3
import numpy as np
import pandas as pd

from abc import abstractmethod
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
        return self.data.loc[self.data.id == int(id)].name.values[0]


class CountryDataHelper(DataHelper):
    pass


class LeagueDataHelper(DataHelper):
    pass


class MatchDataHelper(DataHelper):
    @staticmethod
    def filterMatchesBefore(matches, date, limit):
        if (matches.shape[0] < limit):
            limit = matches.shape[0]
        return matches[matches.date < date].sort_values(
            by="date", ascending=False).iloc[:limit, :]

    @staticmethod
    def filterMatchesByTeamApiId(matches, teamId):
        return matches[(matches.home_team_api_id == teamId) |
                       (matches.away_team_api_id == teamId)]

    @staticmethod
    def filterMatchesByOpponentsTeamIds(matches, team1Id, team2Id):
        team1Matches = matches[
            (matches.home_team_api_id == team1Id) &
            (matches.away_team_api_id == team1Id)
        ]
        team2Matches = matches[
            (matches.home_team_api_id == team2Id) &
            (matches.away_team_api_id == team2Id)
        ]
        return pd.concat([team1Matches, team2Matches])

    @staticmethod
    def getGoalsByTeamId(matches, teamId):
        return \
        int(matches.home_team_goal[matches.home_team_api_id == teamId].sum()) + \
        int(matches.away_team_goal[matches.away_team_api_id == teamId].sum())

    @staticmethod
    def getGoalsConceidedByTeamId(matches, teamId):
        return \
        int(matches.home_team_goal[matches.away_team_api_id == teamId].sum()) + \
        int(matches.away_team_goal[matches.home_team_api_id == teamId].sum())

    @staticmethod
    def getWinsByTeamId(matches, teamId):
        return \
        int(
            matches.home_team_goal[
                (matches.home_team_api_id == teamId) &
                (matches.home_team_goal > matches.away_team_goal)
            ].count()
        ) + \
        int(
            matches.away_team_goal[
                (matches.away_team_api_id == teamId) &
                (matches.away_team_goal > matches.home_team_goal)
            ].count()
        )

    @staticmethod
    def getMatchResult(match):
        matchResult = pd.DataFrame()
        matchResult.loc[0, "match_api_id"] = match.match_api_id
        if match["home_team_goal"] > match["away_team_goal"]:
            matchResult.loc[0, "label"] = "Win"
        elif match["home_team_goal"] < match["away_team_goal"]:
            matchResult.loc[0, "label"] = "Defeat"
        else:
            matchResult.loc[0, "label"] = "Draw"
        return matchResult.loc[0]


class TeamDataHelper(DataHelper):
    def getLongTeamNameByApiId(self, id):
        return self.data.loc[self.data.team_api_id == id].team_long_name.values[0]


class PlayerDataHelper(DataHelper):
    def getPlayerNameByApiId(self, id):
        return self.data.loc[self.data.player_api_id == id].player_name.values[0]


class PlayerAttributeDataHelper(DataHelper):
    def getPlayerRatings(self, match):
        players = list()
        for i in range(1, 12):
            players.append("home_player_{}".format(i))
            players.append("away_player_{}".format(i))

        playerRatings = pd.DataFrame()
        for player in players:
            playerStats = self.data[self.data.player_api_id == match[player]]
            playerStats = playerStats[
                playerStats.date < match["date"]].sort_values(
                    by="date", ascending=False)[:1]

            if np.isnan(match[player]):
                overallPlayerRating = pd.Series(0)
            else:
                playerStats.reset_index(inplace=True, drop=True)
                overallPlayerRating = pd.Series(
                    playerStats.loc[0, "overall_rating"])

            playerRatings = pd.concat(
                [playerRatings, overallPlayerRating], axis=1)

        columnNames = []
        for i in range(1, 12):
            columnNames.append("home_player_{}_overall_rating".format(i))
            columnNames.append("away_player_{}_overall_rating".format(i))
        playerRatings.columns = columnNames
        playerRatings["match_api_id"] = match.match_api_id
        return playerRatings.iloc[0]


class MatchResultPredictDataAggregator(object):
    def __init__(self, database):
        self.database = database
        self.matchData = self.database.runQuery("SELECT * FROM Match;")
        self.countryData = self.database.runQuery("SELECT * FROM Country;")
        self.leagueData = self.database.runQuery("SELECT * FROM League;")
        self.teamData = self.database.runQuery("SELECT * FROM Team;")
        self.playerData = self.database.runQuery("SELECT * FROM Player;")
        self.playerAttributeData = self.database.runQuery(
            "SELECT * FROM Player_Attributes")
        self.countryDataHelper = CountryDataHelper(self.countryData)
        self.leagueDataHelper = LeagueDataHelper(self.leagueData)
        self.teamDataHelper = TeamDataHelper(self.teamData)
        self.playerDataHelper = PlayerDataHelper(self.playerData)
        self.matchDataHelper = MatchDataHelper(self.matchData)
        self.playerAttributeDataHelper = PlayerAttributeDataHelper(
            self.playerAttributeData)
        self.aggregatedData = copy.deepcopy(self.matchData)

    def addCountryNameToMatches(self):
        for match in range(len(self.aggregatedData)):
            self.aggregatedData.loc[match, "country_name"] = self.countryDataHelper.getNameById(
                self.aggregatedData.country_id.iloc[match]
            )

    def addLeagueNameToMatches(self):
        for match in range(len(self.aggregatedData)):
            self.aggregatedData.loc[match, "league_name"] = self.leagueDataHelper.getNameById(
                self.aggregatedData.league_id.iloc[match]
            )

    def addTeamNameToMatches(self, teamType):
        for match in range(len(self.aggregatedData)):
            self.aggregatedData.loc[match, "{}_team_name".format(teamType)] = self.teamDataHelper.getLongTeamNameByApiId(
                self.aggregatedData["{}_team_api_id".format(
                    teamType)].iloc[match]
            )

    def addPlayerNameToMatches(self, teamType, playerId):
        for match in range(len(self.aggregatedData)):
            self.aggregatedData.loc[match, "{}_player_{}".format(teamType, playerId)] = self.playerDataHelper.getPlayerNameByApiId(
                self.aggregatedData["{}_player_{}".format(
                    teamType, playerId)].iloc[match]
            )

    def aggregate(self):
        # import pdb
        # pdb.set_trace()

        self.addCountryNameToMatches()
        self.addLeagueNameToMatches()
        self.addTeamNameToMatches("home")
        self.addTeamNameToMatches("away")
        # for i in range(1, 12):
        #     self.addPlayerNameToMatches("home", i)
        #     self.addPlayerNameToMatches("away", i)

        # rows = ["country_id", "league_id", "season", "stage", "date", "match_api_id", "home_team_api_id",
        #         "away_team_api_id", "home_team_goal", "away_team_goal", "home_player_1", "home_player_2",
        #         "home_player_3", "home_player_4", "home_player_5", "home_player_6", "home_player_7",
        #         "home_player_8", "home_player_9", "home_player_10", "home_player_11", "away_player_1",
        #         "away_player_2", "away_player_3", "away_player_4", "away_player_5", "away_player_6",
        #         "away_player_7", "away_player_8", "away_player_9", "away_player_10", "away_player_11"]
        # self.aggregatedData.dropna(subset=rows, inplace=True)
        # self.aggregatedData = self.aggregatedData.tail(1500)
        # print("Aditya")
        # print("Khursale")

        # player_stats_data = pd.read_sql("SELECT * FROM Player_Attributes;", conn)

        # match_data = match_data.tail(1500)
        # fifa_data = match_data.apply(lambda x :get_fifa_stats(x, player_stats), axis = 1)


if __name__ == "__main__":
    print("Starting...")
    dataAggregator = MatchResultPredictDataAggregator(EuropeanSoccerDatabase())
    dataAggregator.aggregate()
