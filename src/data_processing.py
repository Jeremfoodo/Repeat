import pandas as pd
import gdown
import os

# URL de Google Drive pour le fichier volumineux
gdrive_files = {
    'prepared_data': 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
}

def download_prepared_data():
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    for key, url in gdrive_files.items():
        output = os.path.join(data_dir, f"{key}.csv")
        gdown.download(url, output, quiet=False)

def load_data():
    data_dir = 'data'
    historical_files = {
        'FR': os.path.join(data_dir, 'historical_retention_analysis_FR.csv'),
        'US': os.path.join(data_dir, 'historical_retention_analysis_US.csv'),
        'BE': os.path.join(data_dir, 'historical_retention_analysis_BE.csv'),
        'GB': os.path.join(data_dir, 'historical_retention_analysis_GB.csv')
    }

    historical_data = {country: pd.read_csv(file) for country, file in historical_files.items()}
    df = pd.read_csv(os.path.join(data_dir, 'prepared_data.csv'), parse_dates=['date 1ere commande (Restaurant)', 'Date de commande'], decimal='.')
    
    to_exclude_commande = ['CANCELLED', 'ABANDONED', 'FAILED', 'WAITING']
    to_exclude_paiement = ['CANCELLED', 'ERROR']
    df = df[~df['Statut commande'].isin(to_exclude_commande)]
    df = df[~df['Statut paiement'].isin(to_exclude_paiement)]
    df = df[~df['Canal'].str.contains('trading', case=False, na=False)]
    df['Mois'] = df['Date de commande'].dt.strftime('%Y-%m')
    
    return historical_data, df

def reassign_account_manager(df):
    df = df.sort_values(by=['Restaurant ID', 'Date de commande'])
    df['Owner email'] = df.groupby('Restaurant ID')['Owner email'].transform(lambda x: x.ffill().bfill())
    return df

def filter_data_by_account(df, account_manager):
    return df[df['Owner email'] == account_manager]
