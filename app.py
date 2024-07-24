import streamlit as st
from src.data_processing import load_data, load_recent_purchases, load_objectifs
from segmentation import segmentation_page
from client_info import client_info_page
from global_analysis import global_analysis_page
from account_analysis import account_analysis_page
from active_users import active_users_page
from objectifs import objectifs_page


# Charger les données
historical_data, df = load_data()
df_recent_purchases = load_recent_purchases()
objectifs_df = load_objectifs()

# Extraire les paramètres de requête
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["Segmentation"])[0]
client_id = query_params.get("client_id", [None])[0]

# Afficher la page en fonction du paramètre 'page'
if page == "Segmentation":
    segmentation_page(df)
elif page == "Global Analysis":
    global_analysis_page(df)
elif page == "Account Analysis":
    account_analysis_page(df)
elif page == "Active Users":
    active_users_page(historical_data, df)
elif page == "Objectifs":
    objectifs_page(df)
elif page == "Client Info" and client_id:
    client_info_page(df, df_recent_purchases, int(client_id))
else:
    st.error("Page not found")
