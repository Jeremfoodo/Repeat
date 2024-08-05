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
    
    # Ensure 'date 1ere commande (Restaurant)' is in datetime format
    df['date 1ere commande (Restaurant)'] = pd.to_datetime(df['date 1ere commande (Restaurant)'], format='%Y-%m-%d %H:%M:%S')
    
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=6)).strftime('%Y-%m')]
    
    segment_counts = {
        'Restaurant ID': [],
        'Segment': [],
        'Nombre de Clients': []
    }
    
    for seg_name, seg_df in zip(
        ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients'],
        [acquisition, nouveaux_clients, clients_recents, anciens_clients]
    ):
        segment_counts['Restaurant ID'].extend(seg_df['Restaurant ID'].unique())
        segment_counts['Segment'].extend([seg_name] * seg_df['Restaurant ID'].nunique())
        segment_counts['Nombre de Clients'].extend([seg_df['Restaurant ID'].nunique()])

    # Ensure all lists in segment_counts are of the same length
    max_length = max(len(segment_counts['Restaurant ID']), len(segment_counts['Segment']), len(segment_counts['Nombre de Clients']))
    for key in segment_counts:
        while len(segment_counts[key]) < max_length:
            segment_counts[key].append(None)
    
    results_df = pd.DataFrame(segment_counts)
    results_df['Mois'] = target_month
    return results_df


@st.cache_data
def process_region_data(df, country_code, region):
    df_region = df[(df['Pays'] == country_code) & (df['region'] == region)]
    
    today = datetime.today()
    current_month = today.replace(day=1)
    start_month = (current_month - pd.DateOffset(months=2)).strftime('%Y-%m')
    recent_months = pd.date_range(start=start_month, end=current_month, freq='MS').strftime('%Y-%m').tolist()
    recent_results = pd.concat([calculate_segments_for_month(df_region, month) for month in recent_months], ignore_index=True)
    
    return recent_results

def get_segment_and_spending_info(df, target_month):
    customer_spending = segment_customers(df, *map(int, target_month.split('-')))
    segments_info = calculate_segments_for_month(df, target_month)
    
    # Ensure both DataFrames have 'Restaurant ID'
    if 'Restaurant ID' not in customer_spending.columns:
        raise KeyError("'Restaurant ID' not found in customer_spending DataFrame")
    if 'Restaurant ID' not in segments_info.columns:
        raise KeyError("'Restaurant ID' not found in segments_info DataFrame")
    
    merged_info = pd.merge(customer_spending, segments_info, on='Restaurant ID', how='left')
    
    return merged_info
