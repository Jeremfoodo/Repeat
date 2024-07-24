import streamlit as st
from src.data_processing import load_data, download_prepared_data, load_recent_purchases
from segmentation import segmentation_page
from client_info import client_info_page

# Charger les données
df = load_data()
df_recent_purchases = load_recent_purchases()

# Définir les pages
selected = st.sidebar.selectbox("Sélectionner une page", ["Segmentation", "Client Info"])

# Afficher la page correspondante
if selected == "Segmentation":
    segmentation_page(df)
elif selected == "Client Info":
    query_params = st.experimental_get_query_params()
    if 'client_id' in query_params:
        client_id = int(query_params['client_id'][0])
        client_info_page(df, df_recent_purchases, client_id)
    else:
        st.write("Veuillez sélectionner un client depuis la page Segmentation.")
