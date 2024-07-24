import streamlit as st
import pandas as pd
import plotly.express as px
import gdown

# Charger les données (à partir du cache ou d'une source de données)
@st.cache_data
def load_data():
    # Remplacez par le chemin d'accès à vos données
    url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
    df = pd.read_csv(url, parse_dates=['Date de commande', 'date 1ere commande (Restaurant)'])
    return df

# Charger les données des achats récents en France
@st.cache_data
def load_recent_purchases():
    url = 'https://docs.google.com/spreadsheets/d/1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA/export?format=xlsx'
    df = pd.read_excel(gdown.download(url, None, quiet=False))
    return df

def client_info_page(df, df_recent_purchases, client_id):
    st.title("Informations sur le client")

    client_data = df[df["Restaurant ID"] == client_id]

    if client_data.empty:
        st.error("Aucun client trouvé avec cet ID.")
        return

    # Afficher les informations détaillées du client
    st.subheader(f"Client ID: {client_id}")

    # Analyse des dépenses mensuelles
    client_data['Mois'] = client_data['Date de commande'].dt.to_period('M').astype(str)
    monthly_spending = client_data.groupby('Mois')['Total'].sum().reset_index()
    fig = px.bar(monthly_spending, x='Mois', y='Total', title='Dépenses mensuelles')
    st.plotly_chart(fig)

    # Historique des commandes
    st.subheader("Historique des commandes")
    st.write(client_data[['Date de commande', 'Total', 'Statut commande']])

    # Rechercher les achats récents pour les clients en France
    client_recent_purchases = df_recent_purchases[df_recent_purchases["Restaurant_id"] == client_id]
    
    if not client_recent_purchases.empty:
        st.subheader("Achats récents (3 derniers mois)")

        # Fournisseurs préférés
        suppliers = client_recent_purchases.groupby('Supplier')['GMV'].sum().reset_index()
        fig_suppliers = px.bar(suppliers, x='Supplier', y='GMV', title='Fournisseurs préférés')
        st.plotly_chart(fig_suppliers)

        # Catégories de produits
        product_categories = client_recent_purchases.groupby('Product Category')['GMV'].sum().reset_index()
        fig_categories = px.bar(product_categories, x='Product Category', y='GMV', title='Catégories de produits')
        st.plotly_chart(fig_categories)

        # Produits achetés
        products = client_recent_purchases.groupby('product_name')['quantity_float'].sum().reset_index()
        fig_products = px.bar(products, x='product_name', y='quantity_float', title='Produits achetés')
        st.plotly_chart(fig_products)

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
    
    if spending_category == 'High Spenders':
        st.write("Félicitations ! Ce client est déjà un High Spender. Pensez à lui offrir des récompenses ou des offres exclusives.")
    else:
        if total_spent < 1000:
            st.write("Proposez des réductions ou des offres spéciales pour inciter le client à augmenter ses achats.")
        if num_orders < 5:
            st.write("Encouragez le client à passer plus de commandes en lui proposant des produits complémentaires ou des promotions.")
        if client_recent_purchases.empty:
            st.write("Le client n'a pas fait d'achats récents. Contactez-le pour comprendre les raisons et proposer des solutions.")

# Charger les données
df = load_data()
df_recent_purchases = load_recent_purchases()

# Appeler la fonction de la page d'informations sur le client
client_info_page(df, df_recent_purchases, 44290)
