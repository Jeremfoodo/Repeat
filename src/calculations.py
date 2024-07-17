import pandas as pd
import numpy as np
def calculate_segments_for_month(df, target_month):
    # Calculate previous month
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')
    # Filter orders for the target month
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    # Filter for clients who placed their first order in the target month
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    # Filter for clients who placed their first order in the previous month
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    # Filter for clients who placed their first order between 1st of February until the last day of May
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    # Filter for clients who placed their first order before January (anciens clients)
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    # Count number of unique clients for each segment
    segment_counts = {
        'Segment': ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients'],
        'Nombre de Clients': [
            len(acquisition['Restaurant ID'].unique()),
            len(nouveaux_clients['Restaurant ID'].unique()),
            len(clients_recents['Restaurant ID'].unique()),
            len(anciens_clients['Restaurant ID'].unique())
        ]
    }
    # Calculate number of possible clients in the previous month for each segment
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
    # Calculate number of active clients in the previous month for each segment
    previous_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == previous_month]
    acquisition_previous = 0  # Since acquisition is defined as new clients in the current month
    new_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]['Restaurant ID'].unique())
    recent_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(previous_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(1, 5)]
    )]['Restaurant ID'].unique())
    old_clients_previous = len(previous_orders[previous_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=4)).strftime('%Y-%m')]['Restaurant ID'].unique())
    segment_counts['Nombre de Clients Actifs (Mois Précédent)'] = [
        acquisition_previous,
        new_clients_previous,
        recent_clients_previous,
        old_clients_previous
    ]
    # Calculate percentage ratio
    segment_counts['Rapport (%)'] = np.round(np.divide(segment_counts['Nombre de Clients'], segment_counts['Nombre de Clients Actifs (Mois Précédent)'], out=np.zeros_like(segment_counts['Nombre de Clients'], dtype=float), where=np.array(segment_counts['Nombre de Clients Actifs (Mois Précédent)']) != 0) * 100, 1)
    # Create DataFrame with results
    results_df = pd.DataFrame(segment_counts)
    results_df['Mois'] = target_month
    return results_df
