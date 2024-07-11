import pandas as pd

def load_data():
    historical_files = {
        'FR': 'data/historical_retention_analysis_FR.csv',
        'US': 'data/historical_retention_analysis_US.csv',
        'BE': 'data/historical_retention_analysis_BE.csv',
        'GB': 'data/historical_retention_analysis_GB.csv'
    }

    historical_data = {country: pd.read_csv(file) for country, file in historical_files.items()}
    df = pd.read_csv('data/prepared_data.csv', parse_dates=['date 1ere commande (Restaurant)', 'Date de commande'], decimal='.')
    
    to_exclude_commande = ['CANCELLED', 'ABANDONED', 'FAILED', 'WAITING']
    to_exclude_paiement = ['CANCELLED', 'ERROR']
    df = df[~df['Statut commande'].isin(to_exclude_commande)]
    df = df[~df['Statut paiement'].isin(to_exclude_paiement)]
    df = df[~df['Canal'].str.contains('trading', case=False, na=False)]
    df['Mois'] = df['Date de commande'].dt.strftime('%Y-%m')
    
    return historical_data, df
