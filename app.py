import streamlit as st
from streamlit_option_menu import option_menu
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page
from active_users import active_users_page
from src.data_processing import load_data, download_prepared_data, reassign_account_manager

# Télécharger et charger les données
download_prepared_data()
historical_data, df = load_data()

# Menu vertical
selected = option_menu(
    "Menu",
    ["Analyse Globale", "Par Account", "Objectifs", "Active Users"],
    icons=["graph-up", "person", "bullseye", "bar-chart"],
    menu_icon="cast",
    default_index=0,
    orientation="vertical",
)

if selected == "Analyse Globale":
    global_analysis(historical_data, df)
elif selected == "Par Account":
    account_analysis(df)
elif selected == "Objectifs":
    objectifs_page(historical_data, df)
elif selected == "Active Users":
    active_users_page(historical_data, df)
