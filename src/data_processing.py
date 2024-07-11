import pandas as pd
import gdown
import os

# URLs de Google Drive pour chaque fichier
gdrive_files = {
    'FR': 'https://drive.google.com/uc?id=<ID_FILE_FR>',
    'US': 'https://drive.google.com/uc?id=<ID_FILE_US>',
    'BE': 'https://drive.google.com/uc?id=<ID_FILE_BE>',
    'GB': 'https://drive.google.com/uc?id=<ID_FILE_GB>',
    'prepared_data': 'https://drive.google.com/uc?id=<ID_PREPARED_DATA>'
}

def download_files():
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    for key, url in gdrive_files.items():
        output = os.path.join(data_dir, f"{key}.csv")
        gdown.download(url, output, quiet=False)

def load_data():
    historical_files = {
        'FR': 'data/FR.csv',
        'US': 'data/US.csv',
        'BE': 'data/BE.csv',
        'GB': 'data/GB.csv'
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

def filter_data_by_account(df, account_email):
    return df[df['Owner email'] == account_email]
