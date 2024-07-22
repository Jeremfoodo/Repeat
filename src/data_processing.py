import pandas as pd
import gdown
import os

# URLs de Google Drive pour chaque fichier
gdrive_files = {
    'FR': 'https://drive.google.com/uc?id=1HSagRx3aiT3Jb9idOYtdINlYfp4SsqUE',
    'US': 'https://drive.google.com/uc?id=1Ls5d_1G9E3XeiktLzZs6MXTxGzRv7jTb',
    'BE': 'https://drive.google.com/uc?id=1pLdrmiP715kfG_7ToVhXKXqp5lo8-X48',
    'GB': 'https://drive.google.com/uc?id=1j_GSC0NtbI1ozRBA1w1Vp9cpfp974syN',
    'prepared_data': 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
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
    
    # Ajout de la colonne 'region' vide pour les pays sans région
    for country in historical_data.keys():
        if country not in ['FR', 'US']:
            historical_data[country]['region'] = pd.NA
    
    df = pd.read_csv('data/prepared_data.csv', parse_dates=['date 1ere commande (Restaurant)', 'Date de commande'], decimal='.')
    
    to_exclude_commande = ['CANCELLED', 'ABANDONED', 'FAILED', 'WAITING']
    to_exclude_paiement = ['CANCELLED', 'ERROR']
    df = df[~df['Statut commande'].isin(to_exclude_commande)]
    df = df[~df['Statut paiement'].isin(to_exclude_paiement)]
    df = df[~df['Canal'].str.contains('trading', case=False, na=False)]
    df['Mois'] = df['Date de commande'].dt.strftime('%Y-%m')
    
    # Ajout de la colonne 'region' vide pour le DataFrame principal
    if 'region' not in df.columns:
        df['region'] = pd.NA
    
    return historical_data, df

def reassign_account_manager(df):
    df = df.sort_values(by=['Restaurant ID', 'Date de commande'])
    df['Owner email'] = df.groupby('Restaurant ID')['Owner email'].transform(lambda x: x.ffill().bfill())
    return df

def filter_data_by_account(df, account_manager):
    return df[df['Owner email'] == account_manager]
