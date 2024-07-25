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

    # Calculer la dernière commande si elle n'existe pas
    if 'Dernière commande' not in df.columns:
        df['Dernière commande'] = df.groupby('Restaurant ID')['Date de commande'].transform('max')
    
    if 'Dernière commande' not in client_data.columns:
        client_data.loc[:, 'Dernière commande'] = client_data['Date de commande'].max()

    # Informations standard du client
    client_name = client_data["Restaurant"].iloc[0]
    total_spending = round(client_data["Total"].sum())
    first_order_date = client_data["date 1ere commande (Restaurant)"].iloc[0]
    last_order_date = client_data["Dernière commande"].iloc[0]
    days_since_last_order = (datetime.now() - last_order_date).days
    days_since_first_order = (datetime.now() - first_order_date).days

    # Déterminer la couleur en fonction des jours depuis la dernière commande
    if days_since_last_order < 7:
        days_box_color = "#d4edda"  # Vert
    elif days_since_last_order < 15:
        days_box_color = "#fff3cd"  # Jaune
    elif days_since_last_order < 30:
        days_box_color = "#ffeeba"  # Orange
    else:
        days_box_color = "#f8d7da"  # Rouge

    # Informations sur les fournisseurs et catégories
    total_categories = client_recent_purchases["Product Category"].nunique()
    if pd.api.types.is_datetime64_any_dtype(client_recent_purchases['Date']):
        july_categories = client_recent_purchases[client_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07']["Product Category"].nunique()
    else:
        july_categories = 0

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
    st.markdown(
        f"""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
            <h2>Informations générales</h2>
            <div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>ID du restaurant</h4>
                    <p>{client_id}</p>
                </div>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Nom du restaurant</h4>
                    <p>{client_name}</p>
                </div>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Total des dépenses</h4>
                    <p>{total_spending} €</p>
                </div>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Date de la première commande</h4>
                    <p>{first_order_date.strftime('%Y-%m-%d')} ({days_since_first_order} jours)</p>
                </div>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Date de la dernière commande</h4>
                    <p>{last_order_date.strftime('%Y-%m-%d')}</p>
                </div>
                <div style='background-color: {days_box_color}; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Nombre de jours depuis la dernière commande</h4>
                    <p>{days_since_last_order}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Afficher les informations sur les fournisseurs et catégories
    categories_list = ", ".join(client_recent_purchases['Product Category'].unique())
    st.markdown(
        f"""
        <div style='background-color: #e9ecef; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h2>Informations sur les fournisseurs et catégories</h2>
            <div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Nombre total de catégories</h4>
                    <p>{total_categories}</p>
                    <p>({categories_list})</p>
                </div>
                <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; flex: 0 0 45%; margin: 10px;'>
                    <h4 style='font-size: 1.2rem;'>Nombre de catégories en juillet 2024</h4>
                    <p>{july_categories}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig_category_spending = px.pie(category_spending, values='GMV', names='sub_cat', title='Dépenses par sous-catégorie (3 derniers mois)')
    st.plotly_chart(fig_category_spending)

    fig_supplier_spending = px.pie(supplier_spending, values='GMV', names='Supplier', title='Dépenses par fournisseur (3 derniers mois)')
    st.plotly_chart(fig_supplier_spending)

    st.markdown(
        f"""
        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h2>Produits les plus fréquemment achetés</h2>
            {top_products.to_html(index=False, classes='dataframe')}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Afficher les recommandations
    st.markdown(
        f"""
        <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h2>Recommandations</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Ajouter les recommandations sous forme de tableau
    rec_df = pd.DataFrame(recommendations)
    st.table(rec_df)

# Charger les données récentes
def load_recent_purchases():
    df_recent_purchases = pd.read_excel("dataFR.xlsx", engine='openpyxl')
    df_recent_purchases['Date'] = pd.to_datetime(df_recent_purchases['Date'], errors='coerce')
    df_recent_purchases.dropna(subset=['Date'], inplace=True)
    return df_recent_purchases

# Code principal pour tester la fonction
if __name__ == "__main__":
    df = pd.read_csv("data.csv")
    df_recent_purchases = load_recent_purchases()
    client_info_page(df, df_recent_purchases, 44290)
