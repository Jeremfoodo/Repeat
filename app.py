import streamlit as st
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page
from active_users import active_users_page
from src.data_processing import load_data, download_files, reassign_account_manager

# Télécharger et charger les données
download_files()
historical_data, df = load_data()

# Menu horizontal
tab1, tab2, tab3, tab4 = st.tabs(["Analyse Globale", "Par Account", "Objectifs", "Active Users"])

with tab1:
    global_analysis(historical_data, df)

with tab2:
    account_analysis(df)

with tab3:
    objectifs_page(historical_data, df)

with tab4:
    active_users_page(historical_data, df)
