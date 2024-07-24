import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données (à partir du cache ou d'une source de données)
@st.cache_data
def load_data():
    # Remplacez par le chemin d'accès à vos données
    url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
    df = pd.read_csv(url, parse_dates=['Date de commande', 'date 1ere commande (Restaurant)'])
    return df

def client_info_page(df):
    st.title("Informations sur le client")

    # Utiliser un Restaurant ID en dur pour le test
    client_id = 44290
    client_data = df[df["Restaurant ID"] == client_id]

    if client_data.empty:
        st.error("Aucun client trouvé avec cet ID.")
        return

    # Afficher les informations détaillées du client
    st.subheader(f"Client ID: {client_id}")

    # Analyse des dépenses mensuelles
    client_data['Mois'] = client_data['Date de commande'].dt.to_period('M')
    monthly_spending = client_data.groupby('Mois')['Total'].sum().reset_index()
    fig = px.bar(monthly_spending, x='Mois', y='Total', title='Dépenses mensuelles')
    st.plotly_chart(fig)

    # Historique des commandes
    st.subheader("Historique des commandes")
    st.write(client_data[['Date de commande', 'Total', 'Statut commande']])



# Charger les données
df = load_data()

# Appeler la fonction de la page d'informations sur le client
client_info_page(df)
