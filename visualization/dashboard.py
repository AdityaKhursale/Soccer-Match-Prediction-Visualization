import streamlit as st
from PIL import Image
import os

from shared.constants import RESOURCES_DIR


def readImage(imgName):
    return Image.open(os.path.join(RESOURCES_DIR, imgName))


NUMBER_OF_PLAYERS_BY_NATIONALITY_IMG = "visualization_1.png"

st.title("CMSC 636 Data Visualization Project Soccer Data Visualtion")


# Unused TODO: Update or Remove
buttonClicked = st.sidebar.button("Click me!")

# TODO: think of better names
st.sidebar.header("Game")
playerDemographicsTicked = st.sidebar.checkbox("Player Demographics")
if (playerDemographicsTicked):
    st.header("Number of Players by Nationality")
    st.image(readImage(NUMBER_OF_PLAYERS_BY_NATIONALITY_IMG))
st.sidebar.header("Tournaments")
st.sidebar.header("Teams")
st.sidebar.header("Players")
st.sidebar.header("Predictions")
