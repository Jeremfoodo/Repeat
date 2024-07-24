import streamlit as st
from src.data_processing import load_data, load_recent_purchases, load_objectifs
from segmentation import segmentation_page
from client_info import client_info_page

# Charger les données
historical_data, df = load_data()
df_recent_purchases = load_recent_purchases()
objectifs_df = load_objectifs()

# Extraire les paramètres de requête
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["segmentation"])[0]
client_id = query_params.get("client_id", [None])[0]

# Afficher la page correspondante
if page == "segmentation":
    segmentation_page(df)
elif page == "client_info" and client_id is not None:
    client_info_page(df, df_recent_purchases, int(client_id))
else:
    st.write("Page non trouvée")
