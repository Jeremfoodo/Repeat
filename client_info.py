import streamlit as st
import pandas as pd

# Charger les données (à partir du cache ou d'une source de données)
@st.cache_data
def load_data():
    # Remplacez par le chemin d'accès à vos données
    url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
    df = pd.read_csv(url, parse_dates=['Date de commande', 'date 1ere commande (Restaurant)'])
    return df

def client_info_page(df):
    st.title("Informations sur le client")

    # Obtenir les paramètres de l'URL
    query_params = st.experimental_get_query_params()
    if "client_id" not in query_params:
        st.error("Aucun client sélectionné.")
        return

    client_id = query_params["client_id"][0]
    client_data = df[df["Restaurant ID"] == client_id]

    if client_data.empty:
        st.error("Aucun client trouvé avec cet ID.")
        return

    # Afficher les informations détaillées du client
    st.subheader(f"Client ID: {client_id}")
    st.write(client_data)

    # Afficher des analyses supplémentaires
    total_spent = client_data["Total"].sum().round(2)
    last_order_date = client_data["Date de commande"].max()
    num_orders = client_data.shape[0]

    st.metric("Total dépensé", f"{total_spent} €")
    st.metric("Dernière commande", last_order_date.strftime('%Y-%m-%d'))
    st.metric("Nombre de commandes", num_orders)

    # Vous pouvez ajouter plus de graphiques et d'analyses spécifiques au client ici

# Charger les données
df = load_data()

# Appeler la fonction de la page d'informations sur le client
client_info_page(df)
