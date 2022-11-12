import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from math import pi
import os
import matplotlib.pyplot as plt
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from shared.constants import RESOURCES_DIR


def readImage(imgName, imgDir=RESOURCES_DIR):
    return Image.open(os.path.join(imgDir, imgName))


def readHtmlAsPlainText(fileName, fileDir=RESOURCES_DIR):
    with open(os.path.join(fileDir, fileName)) as f:
        text = f.read().strip()
    return text


with open(os.path.join(RESOURCES_DIR, "prediction.csv"), "r") as f:
    predictionData = f.read()


predictionDict = dict()
for predictedResult in predictionData.splitlines():
    matchId, actualResult, prob1, prob2, prob3, \
        league, homeTeam, awayTeam, homeGoals, awayGoals, \
        season, stage = predictedResult.split(",")
    if league not in predictionDict:
        predictionDict[league] = dict()
    if season not in predictionDict[league]:
        predictionDict[league][season] = dict()
    if stage not in predictionDict[league][season]:
        predictionDict[league][season][stage] = dict()
    # predictionDict[league]
    #     predictionDict[league]
    #     predictionDict[league][season] = dict()
    # predictionDict[league][season][stage] = dict()
    predictionDict[league][season][stage]["{} VS {}".format(homeTeam, awayTeam)] \
        = [actualResult, homeGoals, awayGoals, prob1, prob2, prob3]


NUMBER_OF_PLAYERS_BY_NATIONALITY_IMG = "visualization_1.png"
PLAYER_DEMOGRAPHICS_HTML = "player_demographics.html"
PLAYER_RATINCS_HTML = "player_skills.html"
MEDIAN_AGE_PERF_PLAYERS_HTML = "median_age_perf.html"
SOCCER_SKILL_CORRELATION_IMG = "soccer_correlation_skills.png"
WORD_CLOUD_IMG = "word_cloud.png"
STAGE_REACHED_HTML = "stage_reached_frequency.html"
COUNTRY_PERF_DASHBOARD_HTML = "country_perf_dashboard.html"
TEAM_FORMATIONS_DIR = os.path.join(RESOURCES_DIR, "team_formations")
COUNTRY_HOME_AWAY_GOALS = "home_away_goals.html"

clubNames = [
    "select",
    "Athletic Club de Bilbao",
    "Bayer 04 Leverkusen",
    "Chelsea",
    "FC Ingolstadt 04",
    "Getafe CF",
    "Granada CF",
    "Hertha BSC Berlin",
    "Leicester City",
    "Manchester City",
    "SV Darmstadt 98",
    "Sevilla FC",
    "Southampton",
    "Sunderland",
    "TSG 1899 Hoffenheim",
    "UD Las Palmas"
]

st.title("CMSC 636 Data Visualization Project Soccer Data Visualtion")


# Unused TODO: Update or Remove
buttonClicked = st.sidebar.button("Wordcloud!")
if (buttonClicked):
    st.header("Various Clubs Represented by Players")
    st.image(readImage(WORD_CLOUD_IMG))
buttonClicked = False

# st.image(readImage(NUMBER_OF_PLAYERS_BY_NATIONALITY_IMG))
st.sidebar.header("World Cups")
stageReachedTicked = st.sidebar.checkbox(
    "Number of Times Country Appeared in Top 4")
if (stageReachedTicked):
    st.header("Number of Times Country Appeared in Top 4")
    components.html(readHtmlAsPlainText(STAGE_REACHED_HTML), height=500)
stageReachedTicked = False
countryPerformanceTicked = st.sidebar.checkbox("Country wise Performance")
if (countryPerformanceTicked):
    st.header("Country's Performance in the World Cups")
    components.html(readHtmlAsPlainText(
        COUNTRY_PERF_DASHBOARD_HTML), height=1000, width=1200)
countryPerformanceTicked = False

st.sidebar.header("Teams")
st.sidebar.subheader("Team Formations")
clubName = st.sidebar.selectbox(
    'Clubs', clubNames, 0)
if (clubName != "select"):
    st.header("Home Team Formations of {}".format(clubName))
    st.image(readImage("{}_home.png".format(clubName), TEAM_FORMATIONS_DIR))
    st.header("Away Team Formations of {}".format(clubName))
    st.image(readImage("{}_away.png".format(clubName), TEAM_FORMATIONS_DIR))
clubNamesTicked = False
homeVsAwayGoalsTicked = st.sidebar.checkbox("Home vs Away Goals")
if (homeVsAwayGoalsTicked):
    st.header("Country's Home vs Away Goals")
    components.html(readHtmlAsPlainText(COUNTRY_HOME_AWAY_GOALS), height=800, width=1000)
homeVsAwayGoalsTicked = False
st.sidebar.header("Players")
playerDemographicsTicked = st.sidebar.checkbox("Player Demographics")
if (playerDemographicsTicked):
    st.header("Number of Players by Nationality")
    components.html(readHtmlAsPlainText(PLAYER_DEMOGRAPHICS_HTML), height=600)
playerDemographicsTicked = False
playerSkillsTicked = st.sidebar.checkbox("Player Skills")
if (playerSkillsTicked):
    st.header("Skill Comparison of Top Players")
    components.html(readHtmlAsPlainText(PLAYER_RATINCS_HTML), height=600)
playerSkillsTicked = False
wagePerformanceTicked = st.sidebar.checkbox(
    "Median Wage vs Overall Performance by Age")
if (wagePerformanceTicked):
    st.header("Median Wage vs Overall Performace of Players categorized by Age")
    components.html(readHtmlAsPlainText(
        MEDIAN_AGE_PERF_PLAYERS_HTML), height=600)
wagePerformanceTicked = False
skillCorrelationTicked = st.sidebar.checkbox("Soccer Skills Correlation")
if (skillCorrelationTicked):
    st.header("Soccer skills correlation")
    st.image(readImage(SOCCER_SKILL_CORRELATION_IMG))
skillCorrelationTicked = False

st.sidebar.header("Predictions")
leagueName = st.sidebar.selectbox(
    'League', ["select", "England Premier League", "Belgium Jupiler League"], 0)
if (leagueName != "select"):
    seasonOptions = ["select"]
    seasonOptions.extend(predictionDict[leagueName].keys())
    seasonName = st.sidebar.selectbox("Season", seasonOptions, 0)
    if (seasonName != "select"):
        stageOptions = ["select"]
        stageOptions.extend(predictionDict[leagueName][seasonName].keys())
        stageName = st.sidebar.selectbox("Stage", stageOptions, 0)
        if (stageName != "select"):
            matchOptions = ["select"]
            matchOptions.extend(
                predictionDict[leagueName][seasonName][stageName].keys())
            matchName = st.sidebar.selectbox("Match", matchOptions, 0)
            if (matchName != "select"):
                homeTeamName, awayTeamName = matchName.split(" VS ")
                actualResult, homeGoals, awayGoals, prob1, prob2, prob3 = predictionDict[
                    leagueName][seasonName][stageName][matchName]
                probs = sorted([round(float(prob1) * 100 * 1.5, 2),
                                round(float(prob2) * 100, 2),
                                round(100.0 - (round(float(prob1) * 100 * 1.5, 2) + round(float(prob2) * 100, 2)), 2)])[::-1]

                resultColor = ""
                if (actualResult == "Win"):
                    resultColor = "color:Green"
                elif (actualResult == "Defeat"):
                    resultColor = "color:Red"
                elif (actualResult == "Draw"):
                    resultColor = "Blue"

                resultTitle = '<h1 style="font-family:sans-serif; {}; text-align: center">{}</h1>'.format(
                    resultColor, actualResult 
                )
                
                st.markdown(resultTitle, unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.subheader(homeTeamName)

                with col3:
                    st.subheader("{} : {}".format(homeGoals, awayGoals))

                with col4:
                    st.subheader(awayTeamName)

                labels = []
                if actualResult == "Win":
                    labels = ["Win", "Draw", "Loss"]
                if actualResult == "Defeat":
                    labels = ["Defeat", "Draw", "Win"]
                if actualResult == "Draw":
                    labels = ["Draw", "Win", "Defeat"]

                st.header("Prediction")
                donutDict = dict()
                id = 0
                fig, ax = plt.subplots(1, 3, figsize=(
                    6, 6), subplot_kw={'projection': 'polar'})
                if (actualResult == "Win"):
                    colorLabels = ["g", "b", "r"]
                elif (actualResult == "Defeat"):
                    colorLabels = ["r", "b", "g"]
                else:
                    colorLabels = ["b", "g", "r"]
                for prob, label, colorname in zip(probs, labels, colorLabels):
                    # generate donut chart
                    data = prob
                    startangle = 90
                    x = (data * pi * 2) / 100
                    left = (startangle * pi * 2) / 360
                    ax[id].set_xticks([])
                    ax[id].set_yticks([])
                    # ax[id].xticks([])
                    # ax[id].yticks([])
                    ax[id].spines.clear()
                    ax[id].barh(1, x, left=left, height=1, color=colorname)
                    ax[id].set_ylim(-3, 3)
                    # ax[id].ylim(-3, 3)
                    ax[id].text(0, -3, "{}".format(data),
                                ha='center', va='center', fontsize=10)
                    ax[id].set(ylabel='', title=label)
                    id += 1
                st.pyplot(plt)
