# calculations.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

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

# Fonction pour calculer les segments pour un mois donné
def calculate_segments_for_month(df, target_month):
    year, month = map(int, target_month.split('-'))
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=6)).strftime('%Y-%m')]
    
    segments_info = pd.concat([
        acquisition.assign(Segment='Acquisition'),
        nouveaux_clients.assign(Segment='Nouveaux Clients'),
        clients_recents.assign(Segment='Clients Récents'),
        anciens_clients.assign(Segment='Anciens Clients')
    ])
    
    return segments_info[['Restaurant ID', 'Segment']]

# Fonction pour obtenir les informations de segmentation et de niveau de dépense
@st.cache_data
def get_segment_and_spending_info(df, target_month):
    customer_spending = segment_customers(df, *map(int, target_month.split('-')))
    segments_info = calculate_segments_for_month(df, target_month)
    
    merged_info = pd.merge(customer_spending, segments_info, on='Restaurant ID', how='left')
    return merged_info

# Fonction pour obtenir les clients à réactiver
def get_inactive_clients(previous_df, current_df):
    inactive_clients = previous_df[~previous_df['Restaurant ID'].isin(current_df['Restaurant ID'])]
    return inactive_clients

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
    
    customer_spending['Segment'] = np.where(customer_spending['Restaurant ID'].isin(acquisition['Restaurant ID']), 'Acquisition',
                               np.where(customer_spending['Restaurant ID'].isin(nouveaux_clients['Restaurant ID']), 'Nouveaux Clients',
                               np.where(customer_spending['Restaurant ID'].isin(clients_recents['Restaurant ID']), 'Clients Récents', 'Anciens Clients')))
    
    # Compter les clients par segment et niveau de dépense
    heatmap_data = customer_spending.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique'}).reset_index()
    
    # Pivot pour obtenir le format désiré
    heatmap_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Restaurant ID').fillna(0)
    
    total_clients = customer_spending['Restaurant ID'].nunique()
    
    return heatmap_pivot, total_clients, customer_spending
