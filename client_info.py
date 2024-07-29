# client_info.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.calculations import get_clients_by_segment_and_spending
from recommendations import get_recommendations
from src.segmentation import load_segmentation_data


def map_gamme(gamme_value):
    if gamme_value == 1:
        return "à emporter"
    elif gamme_value == 2:
        return "regular"
    elif gamme_value == 3:
        return "chic"
    else:
        return "Non défini"

def client_info_page(df, df_recent_purchases, segmentation_df, default_client_id):
    st.title("Page d'Information Client")

    # Sélection du pays
    country = st.selectbox("Sélectionnez le pays", ['FR', 'US', 'UK', 'BE'])

    # Charger les données en fonction du pays sélectionné
    segmentation_df = load_segmentation_data(country)
    df_recent_purchases = load_recent_purchases(country)

    # Boîte de saisie pour entrer l'ID client
    client_id_input = st.text_input("Entrez l'ID du client (Restaurant ID)", value=default_client_id)
    client_id_button = st.button("Valider")

    # Mettre à jour le client_id en fonction de l'entrée de l'utilisateur
    if client_id_button:
        client_id = int(client_id_input)
    else:
        client_id = default_client_id

    # Sélectionner les données du client
    client_data = df[df['Restaurant ID'] == client_id]

    # Fusionner les données de segmentation avec les données du client
    client_data = pd.merge(client_data, segmentation_df, left_on='Restaurant ID', right_on='Restaurant_id', how='left')

    # Sélectionner les achats récents du client
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

    # Déterminer la couleur de la box en fonction du nombre de jours depuis la dernière commande
    if days_since_last_order < 7:
        last_order_color = "#d4edda"  # Vert
    elif days_since_last_order < 15:
        last_order_color = "#fff3cd"  # Jaune
    elif days_since_last_order < 30:
        last_order_color = "#ffeeba"  # Orange
    else:
        last_order_color = "#f8d7da"  # Rouge

    # Informations de segmentation
    gamme = client_data["Gamme"].iloc[0] if "Gamme" in client_data.columns else "Non défini"
    gamme = map_gamme(gamme)  # Appliquer la transformation

    type_detail = client_data["Type_detail"].iloc[0] if "Type_detail" in client_data.columns else "Non défini"
    type_general = client_data["Type"].iloc[0] if "Type" in client_data.columns else "Non défini"

    # Informations sur les fournisseurs et catégories
    total_categories = client_recent_purchases["Product Category"].nunique()
    categories_list = ", ".join(client_recent_purchases["Product Category"].unique())
    if pd.api.types.is_datetime64_any_dtype(client_recent_purchases['Date']):
        july_categories = client_recent_purchases[client_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07']["Product Category"].nunique()
    else:
        july_categories = 0

    suppliers = client_recent_purchases.groupby('Supplier')['Date'].max().reset_index()

    category_spending = client_recent_purchases.groupby('sub_cat')['GMV'].sum().reset_index()
    supplier_spending = client_recent_purchases.groupby('Supplier')['GMV'].sum().reset_index()
    top_products = client_recent_purchases.groupby(['product_name']).size().reset_index(name='counts').sort_values(by='counts', ascending=False)

    # Algorithme de recommandations basé sur les nouveaux critères

    # Définir les données de juin et juillet en utilisant df_recent_purchases
    client_june_data = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-06')]
    client_july_data = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07')]

    # Calculer les dépenses totales en juin et juillet à partir de df_recent_purchases
    june_spending = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-06')]['GMV'].sum()
    july_spending = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07')]['GMV'].sum()

    # Informations de segmentation
    gamme = client_data["Gamme"].iloc[0]
    type_detail = client_data["Type_detail"].iloc[0]
    type_general = client_data["Type"].iloc[0]

    # Afficher les informations standard du client avec cadre et pictogrammes
    st.markdown(
        """
        <div style='background-color: #f0f4f7; padding: 20px; border-radius: 10px;'>
            <h2>Infos Générales</h2>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/restaurant.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>ID du restaurant</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/restaurant.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Nom du restaurant</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/money.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Total des dépenses</h5>
                        <p style='margin: 0;'>{} €</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/calendar.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Date de la première commande</h5>
                        <p style='margin: 0;'>{} ({} jours)</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/calendar.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Date de la dernière commande</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
                <div style='background-color: {}; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/calendar.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Nombre de jours depuis la dernière commande</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/categorize.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Gamme</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/restaurant.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Type détaillé</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/restaurant.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Type général</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
            </div>
        </div>
        """.format(
            client_id, client_name, total_spending,
            first_order_date.strftime('%Y-%m-%d'), days_since_first_order,
            last_order_date.strftime('%Y-%m-%d'), last_order_color, days_since_last_order,
            gamme, type_detail, type_general
        ),
        unsafe_allow_html=True
    )

    # Calculer le nombre de jours depuis la dernière commande pour chaque fournisseur
    suppliers['Date'] = pd.to_datetime(suppliers['Date'], errors='coerce')
    suppliers.dropna(subset=['Date'], inplace=True)
    suppliers['Days Since Last Order'] = (datetime.now() - suppliers['Date']).dt.days

    # Trier les fournisseurs par date de commande la plus récente
    suppliers = suppliers.sort_values(by='Date', ascending=False)

    # Formater la date pour n'afficher que l'année, le mois et le jour
    suppliers['Date'] = suppliers['Date'].dt.strftime('%Y-%m-%d')

    # Convertir le DataFrame en tableau HTML
    suppliers_table = suppliers.to_html(index=False, classes='styled-table')

    st.markdown(
        """
        <div style='background-color: #e9ecef; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h2>Informations sur les fournisseurs et catégories</h2>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/list.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Nombre total de catégories</h5>
                        <p style='margin: 0;'>{}</p>
                        <small>{}</small>
                    </div>
                </div>
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; display: flex; align-items: center;'>
                    <img src='https://img.icons8.com/ios-filled/50/000000/list.png' width='30' height='30' style='margin-right: 10px;'/>
                    <div>
                        <h5 style='margin: 0;'>Nombre de catégories en juillet 2024</h5>
                        <p style='margin: 0;'>{}</p>
                    </div>
                </div>
            </div>
            <h3 style='font-size: 1.25rem;'>Derniers achats chez les fournisseurs</h3>
            <div style='background-color: #fff; padding: 20px; border-radius: 10px;'>
                {}
            </div>
        </div>
        """.format(total_categories, categories_list, july_categories, suppliers_table),
        unsafe_allow_html=True
    )

    # Créez les graphiques en secteurs
    fig_category_spending = px.pie(category_spending, values='GMV', names='sub_cat', title='Dépenses par sous-catégorie (3 derniers mois)')
    fig_supplier_spending = px.pie(supplier_spending, values='GMV', names='Supplier', title='Dépenses par fournisseur (3 derniers mois)')

    # Afficher les graphiques côte à côte en utilisant les colonnes
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_category_spending)
    
    with col2:
        st.plotly_chart(fig_supplier_spending)

    # Afficher les produits les plus fréquemment achetés sous forme de tableau
    st.markdown(
        """
        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h2>Produits les plus fréquemment achetés</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.table(top_products)

    # Afficher les recommandations
    recommendations = get_recommendations(
        client_recent_purchases,
        client_june_data,
        client_july_data,
        df_recent_purchases,
        segmentation_df,
        client_id
    )

    # Mettre en évidence les différents types de recommandations
    def format_recommendations(rec):
        type_icon = {
            "Augmentation des efforts": "🚀",
            "Maintien des efforts": "✅",
            "Rachat de fruits et légumes": "🍎",
            "Rachat dans d'autres catégories": "🛒",
            "Recommandation de catégories": "📂",
            "Recommandation multicatégorie": "🔀",
            "Augmentation des produits": "💹",
            "Rachat de produits": "🔄",
            "Recommandation basée sur les restaurants similaires": "🏪"
        }

        return f"{type_icon.get(rec['Type'], '')} **{rec['Type']}**: {rec['Recommandation']}"

    st.markdown("### Recommandations avec icônes")
    for rec in recommendations:
        st.markdown(format_recommendations(rec))
    
        # Enlever la date de la dernière commande pour les recommandations de rachat de produits
        if rec['Type'] == "Rachat de produits" and isinstance(rec['Détails'], list):
            for detail in rec['Détails']:
                if 'Dernier achat' in detail:
                    detail.pop('Dernier achat')
            st.table(pd.DataFrame(rec['Détails']))
        elif isinstance(rec['Détails'], list):
            if all(isinstance(i, dict) for i in rec['Détails']):
                st.table(pd.DataFrame(rec['Détails']))
            else:
                st.markdown(f"**Détails:** {', '.join(rec['Détails'])}")
        else:
            st.markdown(f"**Détails:** {rec['Détails']}")

        st.markdown("---")

# Charger les données récentes
def load_recent_purchases(country):
    # Mapping des pays aux fichiers Google Sheets
    country_files = {
        'FR': 'https://docs.google.com/spreadsheets/d/1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA/edit?usp=sharing',
        'US': 'https://docs.google.com/spreadsheets/d/1HsxBxGpq3lSwJKPALDsDNvJXNi6us2j-/edit?usp=sharing',
        'UK': 'https://docs.google.com/spreadsheets/d/1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a/edit?usp=sharing',
        'BE': 'https://docs.google.com/spreadsheets/d/1fqu_YgsovkDrpqV7OsFStusEvM-9axRg/edit?usp=sharing',
        # Ajouter les autres pays ici
    }

    if country in country_files:
        file_url = country_files[country]
    else:
        raise ValueError(f"Country {country} not supported")

    df_recent_purchases = pd.read_excel(file_url, engine='openpyxl')
    df_recent_purchases['Date'] = pd.to_datetime(df_recent_purchases['Date'], errors='coerce')
    df_recent_purchases.dropna(subset=['Date'], inplace=True)
    return df_recent_purchases
