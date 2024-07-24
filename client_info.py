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

    # Produits les plus commandés
    if 'Produit' in client_data.columns:
        top_products = client_data['Produit'].value_counts().reset_index()
        top_products.columns = ['Produit', 'Nombre de commandes']
        st.subheader("Produits les plus commandés")
        st.write(top_products)
    else:
        st.write("La colonne 'Produit' n'existe pas dans les données.")

    # Catégorisation des dépenses
    total_spent = client_data["Total"].sum().round(2)
    last_order_date = client_data["Date de commande"].max()
    num_orders = client_data.shape[0]

    def categorize_customer(spent):
        if spent <= 500:
            return 'Basic'
        elif 500 < spent <= 1500:
            return 'Silver'
        elif 1500 < spent <= 2000:
            return 'Gold'
        else:
            return 'High Spenders'

    spending_category = categorize_customer(total_spent)

    st.metric("Total dépensé", f"{total_spent} €")
    st.metric("Dernière commande", last_order_date.strftime('%Y-%m-%d'))
    st.metric("Nombre de commandes", num_orders)
    st.metric("Catégorie de dépense", spending_category)

    # Recommandations
    st.subheader("Recommandations")
    if spending_category != 'High Spenders':
        st.write("Recommandez des produits pour augmenter la dépense du client.")
    else:
        st.write("Félicitations ! Ce client est déjà un High Spender. Pensez à lui offrir des récompenses ou des offres exclusives.")

# Charger les données
df = load_data()

# Appeler la fonction de la page d'informations sur le client
client_info_page(df)
