import streamlit as st
from streamlit_option_menu import option_menu
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page
from active_users import active_users_page
from segmentation import segmentation_page
from src.data_processing import load_data, download_prepared_data

# Télécharger et charger les données
download_prepared_data()
historical_data, df = load_data()

# Menu vertical
with st.sidebar:
    selected = option_menu(
        "Menu",
        ["Analyse Globale", "Par Account", "Objectifs", "Active Users", "Segmentation"],
        icons=["bar-chart", "person-circle", "target", "graph-up", "grid"],
        menu_icon="cast",
        default_index=0,
    )

# Afficher la page sélectionnée
if selected == "Analyse Globale":
    global_analysis(historical_data, df)
elif selected == "Par Account":
    account_analysis(df)
elif selected == "Objectifs":
    objectifs_page(df)
elif selected == "Active Users":
    active_users_page(historical_data, df)
elif selected == "Segmentation":
    segmentation_page(df)
