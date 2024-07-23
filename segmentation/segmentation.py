import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from src.data_processing import load_data
from src.calculations import calculate_segments_for_month

@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    # Filtrer les commandes pour le mois cible
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]

    # Calculer les segments
    segments = calculate_segments_for_month(df, target_month)
    segments_dict = segments.set_index('Segment')['Nombre de Clients'].to_dict()

    # Calculer les dépenses totales par client
    total_spent = target_orders.groupby('Restaurant ID')['Total'].sum().reset_index()

    # Ajouter les segments et les dépenses aux données
    target_orders = target_orders.merge(total_spent, on='Restaurant ID', suffixes=('', '_Total'))
    target_orders['Segment'] = target_orders['Restaurant ID'].map(lambda x: 'Acquisition' if segments_dict.get('Acquisition', 0) > 0 else 'Nouveaux Clients' if segments_dict.get('Nouveaux Clients', 0) > 0 else 'Clients Récents' if segments_dict.get('Clients Récents', 0) > 0 else 'Anciens Clients')

    # Définir les niveaux de dépense
    def spending_level(spent):
        if spent < 500:
            return 'Basic'
        elif 500 <= spent < 1500:
            return 'Silver'
        elif 1500 <= spent < 2000:
            return 'Gold'
        else:
            return 'High Spenders'

    target_orders['Spending Level'] = target_orders['Total_Total'].apply(spending_level)

    # Compter les clients et les dépenses totales par segment et niveau de dépense
    heatmap_data = target_orders.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique', 'Total_Total': 'sum'}).reset_index()
    heatmap_data = heatmap_data.pivot('Segment', 'Spending Level', 'Restaurant ID')

    return heatmap_data

def generate_heatmap(data, title):
    plt.figure(figsize=(10, 6))
    sns.heatmap(data, annot=True, fmt="d", cmap="YlGnBu")
    plt.title(title)
    st.pyplot(plt)

def segmentation_page(df):
    st.title("Analyse de la Segmentation des Clients Actifs")

    # Dropdown pour sélectionner le pays
    countries = list(df['Pays'].unique()) + ['Tous les pays']
    selected_country = st.selectbox('Sélectionner un pays', countries)

    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Générer les heatmaps pour juin et juillet 2024
    heatmap_data_june = get_clients_by_segment_and_spending(df, '2024-06')
    heatmap_data_july = get_clients_by_segment_and_spending(df, '2024-07')

    col1, col2 = st.columns(2)
    with col1:
        generate_heatmap(heatmap_data_june, "Juin 2024")
    with col2:
        generate_heatmap(heatmap_data_july, "Juillet 2024")

# Appel de la fonction pour créer la page de segmentation
if __name__ == "__main__":
    historical_data, df = load_data()
    segmentation_page(df)
