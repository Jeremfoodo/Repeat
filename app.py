import streamlit as st
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page
from data_processing import load_historical_data, load_recent_data, preprocess_data

# Fonction pour vider le cache
def clear_cache():
    st.cache_data.clear()

# Charger les données historiques et récentes
historical_data = load_historical_data()
df_recent = load_recent_data()
df_recent = preprocess_data(df_recent)

# Barre de navigation
st.sidebar.title("Navigation")
selected = st.sidebar.radio("Go to", ["Analyse Globale", "Par Account", "Objectifs"])

# Pages
if selected == "Analyse Globale":
    global_analysis(historical_data, df_recent)
elif selected == "Par Account":
    account_analysis(df_recent)
elif selected == "Objectifs":
    objectifs_page()

# Bouton pour mettre à jour les données
if st.sidebar.button('Mettre à jour'):
    clear_cache()
    st.experimental_rerun()
