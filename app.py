import streamlit as st
from src.data_processing import load_data, load_recent_purchases, load_objectifs
from segmentation import segmentation_page
from client_info import client_info_page
from analyse_globale import analyse_globale_page
from account_analysis import account_analysis_page
from active_users import active_users_page
from objectifs import objectifs_page

# Charger les données
historical_data, df = load_data()
df_recent_purchases = load_recent_purchases()
objectifs_df = load_objectifs()

# Définir les options du menu
menu_options = ["Analyse Globale", "Segmentation", "Account Analysis", "Active Users", "Objectifs", "Client Info"]
menu_selection = st.sidebar.selectbox("Menu", menu_options)

# Extraire les paramètres de requête
query_params = st.experimental_get_query_params()
page = query_params.get("page", [None])[0]
client_id = query_params.get("client_id", [None])[0]

# Afficher la page correspondante en fonction du menu sélectionné
if menu_selection == "Analyse Globale":
    analyse_globale_page(df)
elif menu_selection == "Segmentation":
    segmentation_page(df)
elif menu_selection == "Account Analysis":
    account_analysis_page(df)
elif menu_selection == "Active Users":
    active_users_page(df)
elif menu_selection == "Objectifs":
    objectifs_page(df)
elif menu_selection == "Client Info" and client_id is not None:
    client_info_page(df, df_recent_purchases, int(client_id))
elif page == "client_info" and client_id is not None:
    client_info_page(df, df_recent_purchases, int(client_id))
else:
    st.write("Sélectionnez une option dans le menu.")
