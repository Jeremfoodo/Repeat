# client_info.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def client_info_page(df, df_recent_purchases, client_id):
    client_data = df[df['Restaurant ID'] == client_id]
    client_recent_purchases = df_recent_purchases[df_recent_purchases['Restaurant_id'] == client_id]

    # Convertir les dates si elles ne sont pas déjà au format datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date 1ere commande (Restaurant)']):
        df['date 1ere commande (Restaurant)'] = pd.to_datetime(df['date 1ere commande (Restaurant)'])
    if not pd.api.types.is_datetime64_any_dtype(df_recent_purchases['Date']):
        df_recent_purchases['Date'] = pd.to_datetime(df_recent_purchases['Date'], errors='coerce')
        df_recent_purchases.dropna(subset=['Date'], inplace=True)

    # Informations standard du client
    client_name = client_data["Restaurant"].iloc[0]
    total_spending = client_data["Total"].sum()
    first_order_date = client_data["date 1ere commande (Restaurant)"].iloc[0]
    last_order_date = client_data["Dernière commande"].iloc[0]
    days_since_last_order = (datetime.now() - last_order_date).days

    # Informations sur les fournisseurs et catégories
    total_categories = client_recent_purchases["Product Category"].nunique()
    july_categories = client_recent_purchases[client_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07']["Product Category"].nunique()
    suppliers = client_recent_purchases.groupby('Supplier')['Date'].max().reset_index()

    category_spending = client_recent_purchases.groupby('sub_cat')['GMV'].sum().reset_index()
    supplier_spending = client_recent_purchases.groupby('Supplier')['GMV'].sum().reset_index()
    top_products = client_recent_purchases.groupby(['product_name']).size().reset_index(name='counts').sort_values(by='counts', ascending=False)

    # Algorithme de recommandations
    recommendations = []

    # Date de dernière commande
    top_fruits_vegetables = top_products[top_products['product_name'].str.contains('Fruits|Légumes', case=False)]
    recommendations.append({
        "Type": "Achat de fruits et légumes",
        "Recommandation": "Il est temps de recommander des fruits et légumes.",
        "Détails": f"Produits populaires: {', '.join(top_fruits_vegetables['product_name'].values)}"
    })

    if days_since_last_order > 15:
        recommendations.append({
            "Type": "Achat dans d'autres catégories",
            "Recommandation": "Recommandez des produits dans d'autres catégories.",
            "Détails": "Il n'a pas commandé depuis plus de 15 jours."
        })

    # Nombre de catégories
    if total_categories == 1:
        num_products = client_recent_purchases['product_name'].nunique()
        if num_products < 4:
            recommendations.append({
                "Type": "Client mono-produit",
                "Recommandation": "Comprendre pourquoi il n'achète qu'un seul type de produit.",
                "Détails": "Il n'achète que peu de produits dans une seule catégorie."
            })
        else:
            categories_to_recommend = ["Boucherie", "Fruits et Légumes", "Crémerie", "Epicerie Salée"]
            categories_not_bought = [cat for cat in categories_to_recommend if cat not in client_recent_purchases['Product Category'].values]
            recommendations.append({
                "Type": "Proposition de nouvelles catégories",
                "Recommandation": "Proposez des produits dans d'autres catégories.",
                "Détails": f"Catégories à recommander: {', '.join(categories_not_bought)}"
            })

    # Afficher les informations standard du client
    st.markdown(f"## Informations du client {client_name}")
    st.markdown(f"**ID du restaurant:** {client_id}")
    st.markdown(f"**Nom du restaurant:** {client_name}")
    st.markdown(f"**Total des dépenses:** {total_spending:.2f} €")
    st.markdown(f"**Date de la première commande:** {first_order_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**Date de la dernière commande:** {last_order_date.strftime('%Y-%m-%d')}")
    st.markdown(f"**Nombre de jours depuis la dernière commande:** {days_since_last_order}")

    # Afficher les informations sur les fournisseurs et catégories
    st.markdown("### Informations sur les fournisseurs et catégories")
    st.markdown(f"**Nombre total de catégories:** {total_categories}")
    st.markdown(f"**Nombre de catégories en juillet 2024:** {july_categories}")
    st.markdown("**Fournisseurs avec date du dernier achat:**")
    st.write(suppliers)

    fig_category_spending = px.pie(category_spending, values='GMV', names='sub_cat', title='Dépenses par sous-catégorie (3 derniers mois)')
    st.plotly_chart(fig_category_spending)

    fig_supplier_spending = px.pie(supplier_spending, values='GMV', names='Supplier', title='Dépenses par fournisseur (3 derniers mois)')
    st.plotly_chart(fig_supplier_spending)

    st.markdown("### Produits les plus fréquemment achetés")
    st.write(top_products)

    # Afficher les recommandations
    st.markdown("### Recommandations")
    for rec in recommendations:
        st.markdown(f"**Type:** {rec['Type']}")
        st.markdown(f"**Recommandation:** {rec['Recommandation']}")
        st.markdown(f"**Détails:** {rec['Détails']}")
        st.markdown("---")

# Charger les données récentes
def load_recent_purchases():
    df_recent_purchases = pd.read_excel("dataFR.xlsx", engine='openpyxl')
    df_recent_purchases['Date'] = pd.to_datetime(df_recent_purchases['Date'], errors='coerce')
    df_recent_purchases.dropna(subset=['Date'], inplace=True)
    return df_recent_purchases
