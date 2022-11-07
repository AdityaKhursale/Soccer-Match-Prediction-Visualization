import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import folium

from math import *
from collections import Counter
from scipy.stats import kde
import os
import sys
#sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from data_aggregator import EuropeanSoccerDatabase
import warnings
warnings.filterwarnings("ignore")



def Display_compo(df_match,title,nb_match):    

    fig, ax = plt.subplots(nb_match//5+1,5,figsize=(30,(nb_match//5+1)*7))
    #fig.tight_layout()
    for n in range(len(df_match)):
        
        match=df_match.iloc[n]
        
        home_players_api_id = list()
        away_players_api_id = list()
        home_players_x = list()
        away_players_x = list()
        home_players_y = list()
        away_players_y = list()


        for i in range(1,12):
            home_players_api_id.append(match['home_player_%d' % i])
            away_players_api_id.append(match['away_player_%d' % i])
            home_players_x.append(match['home_player_X%d' % i])
            away_players_x.append(match['away_player_X%d' % i])
            home_players_y.append(match['home_player_Y%d' % i])
            away_players_y.append(match['away_player_Y%d' % i])

        #Fetch players'names 
        players_api_id = [home_players_api_id,away_players_api_id]
        players_api_id.append(home_players_api_id) # Home
        players_api_id.append(away_players_api_id) # Away
        players_names = [[None]*11,[None]*11]


        

        # con = sqlite3.connect('E:\DV Project\Soccer-Match-Prediction\database\database.sqlite')
        # con.row_factory = sqlite3.Row
        # cur = con.cursor()

        dbHelper = EuropeanSoccerDatabase()
        cur = dbHelper.connection.cursor()
        

        for i in range(2):
            players_api_id_not_none = [x for x in players_api_id[i] if isnan(x)==False]
            request = 'SELECT player_api_id,player_name FROM Player'
            request += ' WHERE player_api_id IN (' + ','.join(map(str, players_api_id_not_none)) + ')'
            cur.execute(request)
            players = cur.fetchall()
            for player in players:
                idx = players_api_id[i].index(player[0])
                name = player[1].split()[-1] # keep only the last name
                players_names[i][idx] = name


        home_players_x = [5 if x==1 else x for x in home_players_x]
        away_players_x = [5 if x==1 else x for x in away_players_x]

        away_players_y=[(element-12)/1.7 for element in away_players_y]
        home_players_y=[(-element+12)/1.7 for element in home_players_y]

        #print(home_players_y)
        #print(home_players_x)
        
        img = plt.imread("https://socialcompare.com/u/1809/terrain-football-v_e8675e323e9595f354c655b7acfb43ec.png")        
        ax = ax.flatten()
        
        ax[n].imshow(img, extent=[0, 10, 7, -7])
        ax[n].scatter(home_players_x, home_players_y,s=480,c='blue',alpha=0.8)
        ax[n].scatter(away_players_x, away_players_y,s=480,c='red',alpha=0.8)

        #legend
        for label, x, y in zip(players_names[1], away_players_x, away_players_y):
            ax[n].annotate(
                label, 
                xy = (x, y), xytext = (-15, 12),
                textcoords = 'offset points', va = 'center')
        for label, x, y in zip(players_names[0], home_players_x, home_players_y):
            ax[n].annotate(
                label, 
                xy = (x, y), xytext = (-15, 12),
                textcoords = 'offset points', va = 'center')

        ax[n].axis('off')

    fig.suptitle(title, fontsize=50,y=0.92)
    return plt