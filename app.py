import streamlit as st
from global_analysis import global_analysis
from account_analysis import account_analysis
from objectifs import objectifs_page

# Fonction pour vider le cache
def clear_cache():
    st.cache_data.clear()

# Barre de navigation
st.sidebar.title("Navigation")
selected = st.sidebar.radio("Go to", ["Analyse Globale", "Par Account", "Objectifs"])

# Pages
if selected == "Analyse Globale":
    global_analysis()
elif selected == "Par Account":
    account_analysis()
elif selected == "Objectifs":
    objectifs_page()

# Bouton pour mettre à jour les données
if st.sidebar.button('Mettre à jour'):
    clear_cache()
    st.experimental_rerun()
