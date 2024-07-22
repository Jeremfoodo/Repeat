import pandas as pd
import gdown
import os
import streamlit as st

# URL de Google Drive pour les fichiers
prepared_data_url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
objectifs_url = 'https://drive.google.com/uc?id=1UaAh3PUaHjBTShTYUGkd-Yw6fUT7TZJN'

@st.cache_data
def download_prepared_data():
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    output_prepared = os.path.join(data_dir, 'prepared_data.csv')
    output_objectifs = os.path.join(data_dir, 'objectifs.xlsx')
    
    gdown.download(prepared_data_url, output_prepared, quiet=False)
    gdown.download(objectifs_url, output_objectifs, quiet=False)

@st.cache_data
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

@st.cache_data
def load_objectifs():
    data_dir = 'data'
    objectifs_df = pd.read_excel(os.path.join(data_dir, 'objectifs.xlsx'), engine='openpyxl')
    return objectifs_df

def reassign_account_manager(df):
    df = df.sort_values(by=['Restaurant ID', 'Date de commande'])
    df['Owner email'] = df.groupby('Restaurant ID')['Owner email'].transform(lambda x: x.ffill().bfill())
    return df

def filter_data_by_account(df, account_manager):
    return df[df['Owner email'] == account_manager]
