import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import os
import sys
import team_formation as tf
import pandas as pd
import time
#sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import data_aggregator as da
from shared.constants import RESOURCES_DIR

dataAggregator = da.MatchResultPredictDataAggregator(da.EuropeanSoccerDatabase())
time.sleep(10)
# dataAggregator.aggregate()

def readImage(imgName, imgDir = RESOURCES_DIR):
    return Image.open(os.path.join(imgDir, imgName))

def call_team_formation():
    print("Getting Called>>>>>>>>>>>>>>>>>>>>")
    league = dataAggregator.leagueData
    country = dataAggregator.countryData
    match = dataAggregator.matchData
    team = dataAggregator.teamData

    league_country = league.merge(country, on='id')
    fr_league_info = league_country.loc[league_country['name_y'] == 'France']

    fr_league_info=fr_league_info.loc[:, fr_league_info.columns != 'country_id']
    fr_league_info.columns=["country_id","league","country"]
    match_fr = match.merge(fr_league_info, on='country_id')
    print("season in the original dataset :",match_fr['season'].unique())
    fr_18=match_fr.loc[match_fr['season'] == '2015/2016']
    team_18=fr_18['home_team_api_id'].unique().tolist()
    team_18=team[team['team_api_id'].isin(team_18)]

    asse_18_dom=fr_18.loc[fr_18['home_team_api_id'] == 9847]
    asse_18_ext=fr_18.loc[fr_18['away_team_api_id'] == 9847]
    asse_18=pd.concat([asse_18_dom,asse_18_ext])
    return tf.Display_compo(asse_18[:19],'Team formation of ASSE during home matches in 2015-16',19)
    


def readHtmlAsPlainText(fileName, fileDir = RESOURCES_DIR):
    with open(os.path.join(fileDir, fileName)) as f:
        text = f.read().strip()
    return text

NUMBER_OF_PLAYERS_BY_NATIONALITY_IMG = "visualization_1.png"
PLAYER_DEMOGRAPHICS_HTML = "player_demographics.html"
PLAYER_RATINCS_HTML = "player_skills.html"

st.title("CMSC 636 Data Visualization Project Soccer Data Visualtion")


# Unused TODO: Update or Remove
buttonClicked = st.sidebar.button("Click me!")

# TODO: think of better names
st.sidebar.header("Game")

    # st.image(readImage(NUMBER_OF_PLAYERS_BY_NATIONALITY_IMG))
st.sidebar.header("Tournaments")
st.sidebar.header("Teams")
teamFormations = st.sidebar.checkbox("Team Formation")
if(teamFormations):
    st.header("Team Formation")
    plt = call_team_formation()
    st.pyplot(plt)
st.sidebar.header("Players")
playerDemographicsTicked = st.sidebar.checkbox("Player Demographics")
if (playerDemographicsTicked):
    st.header("Number of Players by Nationality")
    components.html(readHtmlAsPlainText(PLAYER_DEMOGRAPHICS_HTML), height=600)
playerSkillsTicked = st.sidebar.checkbox("Player Skills")
if (playerSkillsTicked):
    st.header("Skill Comparison of Top Players")
    components.html(readHtmlAsPlainText(PLAYER_RATINCS_HTML), height=600)
st.sidebar.header("Predictions")




