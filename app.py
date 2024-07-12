import streamlit as st
from streamlit_option_menu import option_menu
from src.data_processing import load_data, download_files, reassign_account_manager
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page

# Fonction pour vider le cache
def clear_cache():
    st.cache_data.clear()
    st.experimental_rerun()

# Télécharger et charger les données avec mise en cache
@st.cache_data
def get_data():
    download_files()
    historical_data, df = load_data()
    df = reassign_account_manager(df)
    return historical_data, df

# Interface utilisateur avec Streamlit
st.set_page_config(page_title="Analyse de la Rétention", layout="wide")

# Menu de navigation
selected = option_menu(
    menu_title=None,
    options=["Analyse Globale", "Par Account", "Objectifs"],
    icons=["bar-chart", "person-circle", "bullseye"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

# Télécharger et charger les données
historical_data, df = get_data()

if selected == "Analyse Globale":
    global_analysis(historical_data, df)
elif selected == "Par Account":
    account_analysis(df)
elif selected == "Objectifs":
    objectifs_page()
