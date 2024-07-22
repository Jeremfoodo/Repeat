import pandas as pd
import numpy as np

def calculate_segments_for_month(df, target_month):
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    segment_counts = {
        'Segment': ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients'],
        'Nombre de Clients': [len(acquisition['Restaurant ID'].unique()), len(nouveaux_clients['Restaurant ID'].unique()), len(clients_recents['Restaurant ID'].unique()), len(anciens_clients['Restaurant ID'].unique())]
    }
    all_previous_acquisitions = df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month)]
    all_recent_clients = df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(previous_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(1, 5)]
    ))]
    all_old_clients = df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=5)).strftime('%Y-%m'))]
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
    old_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]['Restaurant ID'].unique())
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

def process_country_data(df, historical_data, country_code, region=None):
    historical_results = historical_data[country_code]
    df_country = df[df['Pays'] == country_code]
    
    if region:
        if 'region' in df_country.columns:
            df_country = df_country[df_country['region'] == region]
        else:
            raise KeyError(f"La colonne 'region' n'existe pas dans le DataFrame. Colonnes disponibles : {df_country.columns}")

    recent_months = pd.date_range(start='2024-04-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
    recent_results = pd.concat([calculate_segments_for_month(df_country, month) for month in recent_months], ignore_index=True)
    all_results = pd.concat([historical_results, recent_results], ignore_index=True)
    
    return all_results

def process_region_data(df, country_code, region):
    df_region = df[(df['Pays'] == country_code) & (df['region'] == region)]
    
    print(f"Processing region data for {region}")
    print(df_region.head())  # Print the first few rows to check the filtered data

    recent_months = pd.date_range(start='2024-06-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
    recent_results = pd.concat([calculate_segments_for_month(df_region, month) for month in recent_months], ignore_index=True)
    
    return recent_results
