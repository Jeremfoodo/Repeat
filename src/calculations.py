import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

# Fonction de segmentation des clients par niveau de dépense
def segment_customers(data, year, month):
    # Convertir 'Date de commande' en datetime
    data['Date de commande'] = pd.to_datetime(data['Date de commande'], format='%Y-%m-%d %H:%M:%S')
    
    # Filtrer les données pour le mois et l'année spécifiés
    filtered_data = data[(data['Date de commande'].dt.year == year) & 
                         (data['Date de commande'].dt.month == month)]
    
    # Calculer le montant total dépensé par chaque client dans le mois spécifié
    customer_spending = filtered_data.groupby('Restaurant ID').agg({
        'Total': 'sum',
        'Restaurant': 'first'  # Obtenir le nom du restaurant
    }).reset_index()
    
    # Définir les critères de segmentation
    def categorize_customer(spent):
        if spent <= 500:
            return 'Basic'
        elif 500 < spent <= 1500:
            return 'Silver'
        elif 1500 < spent <= 2000:
            return 'Gold'
        else:
            return 'High Spenders'
    
    # Appliquer la catégorisation
    customer_spending['Spending Level'] = customer_spending['Total'].apply(categorize_customer)
    
    return customer_spending

# Fonction pour obtenir les clients par segment et niveau de dépense
@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    year, month = map(int, target_month.split('-'))
    customer_spending = segment_customers(df, year, month)
    
    # Définir les segments
    acquisition = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')]
    clients_recents = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=6)).strftime('%Y-%m')]
    
    customer_spending.loc[customer_spending['Restaurant ID'].isin(acquisition['Restaurant ID']), 'Segment'] = 'Acquisition'
    customer_spending.loc[customer_spending['Restaurant ID'].isin(nouveaux_clients['Restaurant ID']), 'Segment'] = 'Nouveaux Clients'
    customer_spending.loc[customer_spending['Restaurant ID'].isin(clients_recents['Restaurant ID']), 'Segment'] = 'Clients Récents'
    customer_spending.loc[customer_spending['Restaurant ID'].isin(anciens_clients['Restaurant ID']), 'Segment'] = 'Anciens Clients'
    
    # Compter les clients par segment et niveau de dépense
    heatmap_data = customer_spending.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique'}).reset_index()
    
    # Pivot pour obtenir le format désiré
    heatmap_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Restaurant ID').fillna(0)
    
    total_clients = customer_spending['Restaurant ID'].nunique()
    
    return heatmap_pivot, total_clients, customer_spending

# Fonction pour obtenir les clients à réactiver
def get_inactive_clients(previous_df, current_df):
    inactive_clients = previous_df[~previous_df['Restaurant ID'].isin(current_df['Restaurant ID'])]
    return inactive_clients

@st.cache_data
def calculate_segments_for_month(df, target_month):
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=6)).strftime('%Y-%m')]
    segment_counts = {
        'Segment': ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients'],
        'Nombre de Clients': [len(acquisition['Restaurant ID'].unique()), len(nouveaux_clients['Restaurant ID'].unique()), len(clients_recents['Restaurant ID'].unique()), len(anciens_clients['Restaurant ID'].unique())]
    }
    all_previous_acquisitions = df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month)]
    all_recent_clients = df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(previous_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(1, 5)]
    ))]
    all_old_clients = df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=6)).strftime('%Y-%m'))]
    segment_counts['Nombre de Clients Possible'] = [
        len(acquisition['Restaurant ID'].unique()),
        len(all_previous_acquisitions['Restaurant ID'].unique()),
        len(all_recent_clients['Restaurant ID'].unique()),
        len(all_old_clients['Restaurant ID'].unique())
    ]
    previous_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == previous_month]
    acquisition_previous = 0
    new_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]['Restaurant ID'].unique())
    recent_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(previous_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(1, 5)]
    )]['Restaurant ID'].unique())
    old_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=6)).strftime('%Y-%m')]['Restaurant ID'].unique())
    segment_counts['Nombre de Clients Actifs (Mois Précédent)'] = [
        acquisition_previous,
        new_clients_previous,
        recent_clients_previous,
        old_clients_previous
    ]
    segment_counts['Rapport (%)'] = np.round(np.divide(segment_counts['Nombre de Clients'], segment_counts['Nombre de Clients Actifs (Mois Précédent)'], out=np.zeros_like(segment_counts['Nombre de Clients'], dtype=float), where=np.array(segment_counts['Nombre de Clients Actifs (Mois Précédent)']) != 0) * 100, 1)
    results_df = pd.DataFrame(segment_counts)
    results_df['Mois'] = target_month
    return results_df

@st.cache_data
def process_country_data(df, historical_data, country_code, region=None):
    historical_results = historical_data[country_code]
    df_country = df[df['Pays'] == country_code]
    
    if region:
        if 'region' in df_country.columns:
            df_country = df_country[df_country['region'] == region]
        else:
            raise KeyError(f"La colonne 'region' n'existe pas dans le DataFrame. Colonnes disponibles : {df_country.columns}")

    today = datetime.today()
    current_month = today.replace(day=1)
    start_month = (current_month - pd.DateOffset(months=3)).strftime('%Y-%m')
    recent_months = pd.date_range(start=start_month, end=current_month, freq='MS').strftime('%Y-%m').tolist()
    recent_results = pd.concat([calculate_segments_for_month(df_country, month) for month in recent_months], ignore_index=True)
    all_results = pd.concat([historical_results, recent_results], ignore_index=True)
    
    return all_results

@st.cache_data
def process_region_data(df, country_code, region):
    df_region = df[(df['Pays'] == country_code) & (df['region'] == region)]
    
    today = datetime.today()
    current_month = today.replace(day=1)
    start_month = (current_month - pd.DateOffset(months=2)).strftime('%Y-%m')
    recent_months = pd.date_range(start=start_month, end=current_month, freq='MS').strftime('%Y-%m').tolist()
    recent_results = pd.concat([calculate_segments_for_month(df_region, month) for month in recent_months], ignore_index=True)
    
    return recent_results
