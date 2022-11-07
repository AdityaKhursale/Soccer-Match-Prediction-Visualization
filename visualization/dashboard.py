import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import os

from shared.constants import RESOURCES_DIR


def readImage(imgName, imgDir = RESOURCES_DIR):
    return Image.open(os.path.join(imgDir, imgName))


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
