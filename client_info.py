# client_info.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.calculations import get_clients_by_segment_and_spending

def client_info_page(df, df_recent_purchases, default_client_id):
    st.title("Page d'Information Client")

    # Boîte de saisie pour entrer l'ID client
    client_id_input = st.text_input("Entrez l'ID du client (Restaurant ID)", value=default_client_id)
    client_id_button = st.button("Valider")

    # Mettre à jour le client_id en fonction de l'entrée de l'utilisateur
    if client_id_button:
        client_id = int(client_id_input)
    else:
        client_id = default_client_id

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

    # Déterminer la couleur de la box en fonction du nombre de jours depuis la dernière commande
    if days_since_last_order < 7:
        last_order_color = "#d4edda"  # Vert
    elif days_since_last_order < 15:
        last_order_color = "#fff3cd"  # Jaune
    elif days_since_last_order < 30:
        last_order_color = "#ffeeba"  # Orange
    else:
        last_order_color = "#f8d7da"  # Rouge

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
    recommendations = []

    # Définir les données de juin et juillet en utilisant df_recent_purchases
    client_june_data = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-06')]
    client_july_data = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07')]

    
    
    # Calculer les dépenses totales en juin et juillet à partir de df_recent_purchases
    june_spending = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-06')]['GMV'].sum()
    july_spending = df_recent_purchases[(df_recent_purchases['Restaurant_id'] == client_id) & (df_recent_purchases['Date'].dt.strftime('%Y-%m') == '2024-07')]['GMV'].sum()


    # Comparer les niveaux de dépense
    if july_spending < june_spending:
        recommendations.append({
            "Type": "Augmentation des efforts",
            "Recommandation": "Le client a baissé ses dépenses en juillet par rapport à juin. Augmentez les efforts de recommandation pour l'inciter à commander plus.",
            "Détails": ""
        })
    elif july_spending > june_spending:
        recommendations.append({
            "Type": "Maintien des efforts",
            "Recommandation": "Le client a augmenté ses dépenses en juillet par rapport à juin. Maintenez ou améliorez les recommandations pour continuer cette tendance.",
            "Détails": ""
        })

    # Fréquence d'achat
    if 'Fruits et Légumes' in client_recent_purchases['Product Category'].values:
        last_fruit_veg_order_date = client_recent_purchases[client_recent_purchases['Product Category'] == 'Fruits et Légumes']['Date'].max()
        last_fruit_veg_order_date = pd.to_datetime(last_fruit_veg_order_date, errors='coerce')  # Convertir en datetime
        if (datetime.now() - last_fruit_veg_order_date).days > 7:
            recommendations.append({
                "Type": "Rachat de fruits et légumes",
                "Recommandation": "Recommandez de racheter des fruits et légumes.",
                "Détails": f"Le dernier achat de fruits et légumes a été effectué il y a {(datetime.now() - last_fruit_veg_order_date).days} jours."
            })
    else:
        last_order_date = client_recent_purchases['Date'].max()
        last_order_date = pd.to_datetime(last_order_date, errors='coerce')  # Convertir en datetime
        if (datetime.now() - last_order_date).days > 15:
            recommendations.append({
                "Type": "Rachat dans d'autres catégories",
                "Recommandation": "Recommandez de racheter dans d'autres catégories.",
                "Détails": f"Le dernier achat a été effectué il y a {(datetime.now() - last_order_date).days} jours."
            })

    # Nombre de catégories
    june_categories = client_june_data['Product Category'].nunique()
    july_categories = client_july_data['Product Category'].nunique()

    # Comparaison juin vs juillet
    if july_categories < june_categories:
        categories_not_bought_in_july = set(client_june_data['Product Category'].unique()) - set(client_july_data['Product Category'].unique())
        recommendations.append({
            "Type": "Recommandation de catégories",
            "Recommandation": "Recommandez des achats dans les catégories non commandées en juillet.",
            "Détails": f"Catégories non commandées en juillet: {', '.join(categories_not_bought_in_july)}"
        })

    # Nombre total de catégories distinctes
    total_categories = client_recent_purchases['Product Category'].nunique()

    if total_categories < 3:
        categories_to_recommend = ["Boucherie", "Fruits et Légumes", "Crémerie", "Epicerie Salée"]
        categories_not_bought = [cat for cat in categories_to_recommend if cat not in client_recent_purchases['Product Category'].values]
        recommendations.append({
            "Type": "Recommandation multicatégorie",
            "Recommandation": "Proposez des produits dans les principales catégories non commandées.",
            "Détails": f"Catégories à recommander: {', '.join(categories_not_bought)}"
        })
    elif total_categories >= 3:
        recommendations.append({
            "Type": "Augmentation des produits",
            "Recommandation": "Focalisez sur l'augmentation du nombre de produits ou des produits plus chers dans les catégories existantes.",
            "Détails": ""
        })

    # Produits fréquemment achetés mais récemment non commandés
    frequently_bought_products = client_recent_purchases.groupby('product_name').size().reset_index(name='counts').sort_values(by='counts', ascending=False)
    for product in frequently_bought_products['product_name'].unique():
        last_product_order_date = client_recent_purchases[client_recent_purchases['product_name'] == product]['Date'].max()
        last_product_order_date = pd.to_datetime(last_product_order_date, errors='coerce')  # Convertir en datetime
        if (datetime.now() - last_product_order_date).days > 30:
            recommendations.append({
                "Type": "Rachat de produit",
                "Recommandation": f"Recommandez de racheter le produit {product}.",
                "Détails": f"Le dernier achat de ce produit a été effectué il y a {(datetime.now() - last_product_order_date).days} jours."
            })


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
            </div>
        </div>
        """.format(
            client_id, client_name, total_spending,
            first_order_date.strftime('%Y-%m-%d'), days_since_first_order,
            last_order_date.strftime('%Y-%m-%d'), last_order_color, days_since_last_order
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

    # Remplacer cette section dans le code existant
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
    st.markdown(
        """
        <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h2>Recommandations</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    recommendations_df = pd.DataFrame(recommendations)
    st.table(recommendations_df)

# Charger les données récentes
def load_recent_purchases():
    df_recent_purchases = pd.read_excel("dataFR.xlsx", engine='openpyxl')
    df_recent_purchases['Date'] = pd.to_datetime(df_recent_purchases['Date'], errors='coerce')
    df_recent_purchases.dropna(subset=['Date'], inplace=True)
    return df_recent_purchases


   
