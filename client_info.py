import streamlit as st
import pandas as pd
import plotly.express as px
import gdown
from datetime import datetime

# Charger les données (à partir du cache ou d'une source de données)
@st.cache_data
def load_data():
    url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
    df = pd.read_csv(url, parse_dates=['Date de commande', 'date 1ere commande (Restaurant)'])
    return df

# Charger les données des achats récents en France
@st.cache_data
def load_recent_purchases():
    url = 'https://docs.google.com/spreadsheets/d/1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA/export?format=xlsx'
    df = pd.read_excel(gdown.download(url, None, quiet=False), parse_dates=['Date'])
    return df

def client_info_page(df, df_recent_purchases, client_id):
    st.title("Informations sur le client")

    client_data = df[df["Restaurant ID"] == client_id]

    if client_data.empty:
        st.error("Aucun client trouvé avec cet ID.")
        return

    # Informations standard du client
    client_name = client_data["Restaurant"].iloc[0]
    total_spent = client_data["Total"].sum().round(2)
    first_order_date = client_data["date 1ere commande (Restaurant)"].min()
    last_order_date = client_data["Date de commande"].max()
    days_since_last_order = (datetime.now() - last_order_date).days
    num_orders = client_data.shape[0]

    # Afficher les informations détaillées du client
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
        <h4>Informations Client</h4>
        <p><strong>ID :</strong> {client_id}</p>
        <p><strong>Nom :</strong> {client_name}</p>
        <p><strong>Total des dépenses :</strong> {total_spent} €</p>
        <p><strong>Date de la première commande :</strong> {first_order_date}</p>
        <p><strong>Date de la dernière commande :</strong> {last_order_date} ({days_since_last_order} jours)</p>
        <p><strong>Nombre de commandes :</strong> {num_orders}</p>
    </div>
    """.format(
        client_id=client_id,
        client_name=client_name,
        total_spent=total_spent,
        first_order_date=first_order_date.strftime('%Y-%m'),
        last_order_date=last_order_date.strftime('%Y-%m-%d'),
        days_since_last_order=days_since_last_order,
        num_orders=num_orders
    ), unsafe_allow_html=True)

    # Rechercher les achats récents pour les clients en France
    client_recent_purchases = df_recent_purchases[df_recent_purchases["Restaurant_id"] == client_id]
    
    if not client_recent_purchases.empty:
        st.subheader("Fournisseurs et Catégories")

        # Infos générales
        total_categories = client_recent_purchases["Product Category"].nunique()
        july_categories = client_recent_purchases[client_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07']["Product Category"].nunique()
        suppliers = client_recent_purchases.groupby('Supplier')['Date'].max().reset_index()
        
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
            <h4>Informations Générales</h4>
            <p><strong>Total des catégories :</strong> {total_categories}</p>
            <p><strong>Catégories différentes en juillet 2024 :</strong> {july_categories}</p>
            <p><strong>Fournisseurs :</strong></p>
            {suppliers_table}
        </div>
        """.format(
            total_categories=total_categories,
            july_categories=july_categories,
            suppliers_table=suppliers.to_html(index=False)
        ), unsafe_allow_html=True)

        # Graphiques en camembert
        subcat_gmv = client_recent_purchases.groupby('sub_cat')['GMV'].sum().reset_index()
        fig_subcat = px.pie(subcat_gmv, values='GMV', names='sub_cat', title='Dépenses par sous-catégorie (3 derniers mois)')
        
        supplier_gmv = client_recent_purchases.groupby('Supplier')['GMV'].sum().reset_index()
        fig_supplier = px.pie(supplier_gmv, values='GMV', names='Supplier', title='Dépenses par fournisseur (3 derniers mois)')
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_subcat)
        with col2:
            st.plotly_chart(fig_supplier)

        # Produits fréquemment achetés
        frequent_products = client_recent_purchases.groupby('product_name')['quantity_float'].sum().reset_index()
        frequent_products = frequent_products.sort_values(by='quantity_float', ascending=False).head(10)
        
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
            <h4>Produits fréquemment achetés</h4>
            {products_table}
        </div>
        """.format(
            products_table=frequent_products.to_html(index=False)
        ), unsafe_allow_html=True)

# Charger les données
df = load_data()
df_recent_purchases = load_recent_purchases()

# Appeler la fonction de la page d'informations sur le client
client_info_page(df, df_recent_purchases, 44290)
