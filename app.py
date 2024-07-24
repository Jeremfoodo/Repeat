import streamlit as st
import pandas as pd
from client_info import client_info_page
from segmentation import segmentation_page
from src.data_processing import load_data, load_recent_purchases

# Charger les données
df = load_data()
df_recent_purchases = load_recent_purchases()

# Extraire les paramètres de requête
query_params = st.experimental_get_query_params()
selected_client_id = query_params.get('client_id', [None])[0]

# Sélectionner la page
selected = st.sidebar.selectbox("Menu", ["Segmentation", "Client Info"])

if selected == "Segmentation":
    segmentation_page(df)
elif selected == "Client Info":
    if selected_client_id:
        client_info_page(df, df_recent_purchases, int(selected_client_id))
    else:
        st.write("Aucun client sélectionné.")
