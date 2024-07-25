import streamlit as st
from streamlit_option_menu import option_menu
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page
from active_users import active_users_page
from segmentation import segmentation_page
from client_info import client_info_page  # Ajouter cette ligne
from src.data_processing import load_data, download_prepared_data, reassign_account_manager, load_recent_purchases, load_segmentation_data
import gdown
import pandas as pd


# Télécharger et charger les données
download_prepared_data()
historical_data, df = load_data()


# Charger les achats récents
@st.cache_data
def load_recent_purchases():
    url = 'https://docs.google.com/spreadsheets/d/1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA/export?format=xlsx'
    df = pd.read_excel(gdown.download(url, None, quiet=False), parse_dates=['Date'])
    return df

df_recent_purchases = load_recent_purchases()

# Menu vertical
with st.sidebar:
    selected = option_menu(
        "Menu",
        ["Analyse Globale", "Par Account", "Objectifs", "Active Users", "Segmentation", "Client Info"],  # Ajouter "Client Info"
        icons=["bar-chart", "person-circle", "target", "graph-up", "grid", "info-circle"],  # Ajouter une icône
        menu_icon="cast",
        default_index=0,
    )

default_client_id = 44290
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
elif selected == "Client Info":  # Ajouter cette section
    client_info_page(df, df_recent_purchases, segmentation_df, default_client_id)  # Appeler la fonction avec un ID de client en dur


