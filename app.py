import streamlit as st
from streamlit_option_menu import option_menu
from src.data_processing import load_data, download_files
from global_analysis import global_analysis
from account_analysis import account_analysis

# Fonction pour vider le cache
def clear_cache():
    st.caching.clear_cache()
    st.experimental_rerun()

# Télécharger et charger les données avec mise en cache
@st.cache(allow_output_mutation=True)
def get_data():
    download_files()
    return load_data()

# Interface utilisateur avec Streamlit
st.set_page_config(page_title="Analyse de la Rétention", layout="wide")

# Menu de navigation
selected = option_menu(
    menu_title=None,
    options=["Analyse Globale", "Par Account"],
    icons=["bar-chart", "person-circle"],
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
