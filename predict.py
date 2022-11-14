import copy

import pandas as pd
import numpy as np
from data_aggregator import (EuropeanSoccerDatabase, MatchDataHelper,
                             MatchResultPredictDataAggregator)
from sklearn import linear_model, model_selection
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt 


def getFeaturesFromMatches(match, matches):
    matchFeatures = pd.DataFrame()
    homeTeamMatches = MatchDataHelper.filterMatchesByTeamApiId(
        matches, match.home_team_api_id
    )
    homeTeamMatches = MatchDataHelper.filterMatchesBefore(
        homeTeamMatches, match.date, 10
    )
    homeTeamGoals = MatchDataHelper.getGoalsByTeamId(
        homeTeamMatches, match.home_team_api_id
    )
    homeTeamGoalsConceided = MatchDataHelper.getGoalsConceidedByTeamId(
        homeTeamMatches, match.home_team_api_id
    )
    homeTeamWins = MatchDataHelper.getWinsByTeamId(
        homeTeamMatches, match.home_team_api_id
    ) 

    awayTeamMatches = MatchDataHelper.filterMatchesByTeamApiId(
        matches, match.away_team_api_id
    )
    awayTeamMatches = MatchDataHelper.filterMatchesBefore(
        awayTeamMatches, match.date, 10
    )
    awayTeamGoals = MatchDataHelper.getGoalsByTeamId(
        awayTeamMatches, match.away_team_api_id
    )
    awayTeamGoalsConceided = MatchDataHelper.getGoalsConceidedByTeamId(
        awayTeamMatches, match.home_team_api_id
    )
    awayTeamWins = MatchDataHelper.getWinsByTeamId(
        awayTeamMatches, match.away_team_api_id
    ) 

    againstMatches = MatchDataHelper.filterMatchesByOpponentsTeamIds(
        matches, match.home_team_api_id, match.away_team_api_id
    )
    againstMatches = MatchDataHelper.filterMatchesBefore(
        againstMatches, match.date, 3
    )
    matchesWonAgainstAwayTeam = MatchDataHelper.getWinsByTeamId(
        againstMatches, match.home_team_api_id
    )
    matchesLostAgainstAwayTeam = MatchDataHelper.getWinsByTeamId(
        againstMatches, match.away_team_api_id
    ) 

    matchFeatures.loc[0, "match_api_id"] = match.match_api_id
    matchFeatures.loc[0, "league_id"] = match.league_id
    matchFeatures.loc[0, "home_team_goals_difference"] = homeTeamGoals - homeTeamGoalsConceided
    matchFeatures.loc[0, "away_team_goals_difference"] = awayTeamGoals - awayTeamGoalsConceided
    matchFeatures.loc[0, "games_won_home_team"] = homeTeamWins
    matchFeatures.loc[0, "games_won_away_team"] = awayTeamWins
    matchFeatures.loc[0, "games_against_won"] = matchesWonAgainstAwayTeam
    matchFeatures.loc[0, "games_against_lost"] = matchesLostAgainstAwayTeam

    return matchFeatures.loc[0]


def plotAccuracyComparison(classifiers, trainAccuracies, testAccuracies):
    xAxis = np.arange(len(classifiers))
    trainAccuracies = [x * 100 for x in trainAccuracies]
    testAccuracies = [x * 100 for x in testAccuracies]
    plt.figure(figsize=(10, 8))
    plt.bar(xAxis - 0.2, trainAccuracies, 0.4, label="Training Accuracy")
    plt.bar(xAxis + 0.2, testAccuracies, 0.4, label="Test Accuracy")
    
    plt.xticks(xAxis, classifiers)
    plt.xlabel("Classifiers")
    plt.ylabel("Accuracy Score")
    plt.title("Comparison of Classifier Accuracies")
    plt.legend()
    plt.savefig("classifier_accuracy_comaparison.png")


if __name__ == "__main__":
    dataAggregator = MatchResultPredictDataAggregator(EuropeanSoccerDatabase())
    columnsOfInterest = [
        "country_id",
        "league_id",
        "season",
        "stage",
        "date",
        "match_api_id",
        "home_team_api_id",
        "away_team_api_id",
        "home_team_goal",
        "away_team_goal",
    ]
    
    for i in range(1, 12):
        columnsOfInterest.append("home_player_{}".format(i))
        columnsOfInterest.append("away_player_{}".format(i))
    trainingMatchData = copy.deepcopy(dataAggregator.matchData)
    trainingMatchData.dropna(subset=columnsOfInterest, inplace=True)
    trainingMatchData = trainingMatchData.head(1500)
    playerRatingsData = trainingMatchData.apply(
        lambda match: dataAggregator.playerAttributeDataHelper.getPlayerRatings(
            match
        ), axis=1
    )

    matchFeatures = trainingMatchData.apply(lambda match: getFeaturesFromMatches(match, trainingMatchData), axis=1)
    leagueIdFeatures = pd.get_dummies(matchFeatures['league_id']).rename(
        columns=lambda leagueId: "League_{}".format(str(leagueId))
    )
    matchFeatures = pd.concat([matchFeatures, leagueIdFeatures], axis=1)
    matchFeatures.drop(["league_id"], inplace=True, axis=1)

    matchResults = trainingMatchData.apply(
        dataAggregator.matchDataHelper.getMatchResult, axis=1)
    
    features = pd.merge(
        matchFeatures, playerRatingsData,
        on="match_api_id", how="left"
    )
    features = pd.merge(
        features, matchResults,
        on="match_api_id", how="left"
    )
    features.dropna(inplace=True)

    labels = features.loc[:, "label"]
    features = features.drop("match_api_id", axis=1)
    features = features.drop("label", axis=1)
    xTrain, xTest, yTrain, yTest = model_selection.train_test_split(
        features, labels
    )

    adaboostClassifier = AdaBoostClassifier(
        n_estimators = 200, random_state = 2)
    gaussianNBClassifier = GaussianNB()
    kNeighborsClassifier =  KNeighborsClassifier()
    logisticRegressionClassifier = linear_model.LogisticRegression(
        multi_class = "ovr", solver = "sag", class_weight = 'balanced')

    classifiers = [
        adaboostClassifier,
        gaussianNBClassifier,
        kNeighborsClassifier,
        logisticRegressionClassifier
    ]

    classifierNames = []
    trainAccuracies = []
    testAccuracies = []
    for classifier in classifiers:
        classifier.fit(xTrain, yTrain)
        classifierName = classifier.__class__.__name__
        trainAccuracy = accuracy_score(yTrain, classifier.predict(xTrain))
        testAccuracy = accuracy_score(yTest, classifier.predict(xTest))
        print(
            "Accuracy of {} for training set: {:.4f}.".format(
                classifierName, trainAccuracy
            )
        )
        print(
            "Accuracy of {} for test set: {:.4f}.".format(
                classifierName, testAccuracy
            )
        )

        classifierNames.append(classifierName)
        trainAccuracies.append(trainAccuracy)
        testAccuracies.append(testAccuracy)
    
    plotAccuracyComparison(classifierNames, trainAccuracies, testAccuracies)
