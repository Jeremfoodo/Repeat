import pandas as pd
import gdown
import os
import streamlit as st

# URL de Google Drive pour les fichiers
prepared_data_url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
objectifs_url = 'https://drive.google.com/uc?id=17TDM9d4MqXxmj1JC4pv0G9nDjRqKEtXK'
recent_purchases_url = 'https://docs.google.com/spreadsheets/d/1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA/export?format=xlsx'
segmentation_url = 'https://drive.google.com/uc?id=1lCVTDYtM_SWj1W5OqTr15-56K4BCWPqf'

@st.cache_data
def download_prepared_data():
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    output_prepared = os.path.join(data_dir, 'prepared_data.csv')
    output_objectifs = os.path.join(data_dir, 'objectifs.xlsx')
    output_recent_purchases = os.path.join(data_dir, 'dataFR.xlsx')
    output_segmentation = os.path.join(data_dir, 'segmentation_data.xlsx')
    
    if not os.path.exists(output_prepared):
        gdown.download(prepared_data_url, output_prepared, quiet=False)
    if not os.path.exists(output_objectifs):
        gdown.download(objectifs_url, output_objectifs, quiet=False)
    if not os.path.exists(output_recent_purchases):
        gdown.download(recent_purchases_url, output_recent_purchases, quiet=False)
    if not os.path.exists(output_segmentation):
        gdown.download(segmentation_url, output_segmentation, quiet=False)

@st.cache_data
def load_data():
    data_dir = 'data'
    
    # Vérifier et télécharger les données préparées si nécessaire
    download_prepared_data()

    historical_files = {
        'FR': os.path.join(data_dir, 'historical_retention_analysis_FR.csv'),
        'US': os.path.join(data_dir, 'historical_retention_analysis_US.csv'),
        'BE': os.path.join(data_dir, 'historical_retention_analysis_BE.csv'),
        'GB': os.path.join(data_dir, 'historical_retention_analysis_GB.csv')
    }

    historical_data = {}
    for country, file in historical_files.items():
        df = pd.read_csv(file)
        df['Pays'] = country
        historical_data[country] = df
    
    df = pd.read_csv(os.path.join(data_dir, 'prepared_data.csv'), parse_dates=['date 1ere commande (Restaurant)', 'Date de commande'], decimal='.')
    
    to_exclude_commande = ['CANCELLED', 'ABANDONED', 'FAILED', 'WAITING']
    to_exclude_paiement = ['CANCELLED', 'ERROR']
    df = df[~df['Statut commande'].isin(to_exclude_commande)]
    df = df[~df['Statut paiement'].isin(to_exclude_paiement)]
    df = df[~df['Canal'].str.contains('trading', case=False, na=False)]
    df['Mois'] = df['Date de commande'].dt.strftime('%Y-%m')
    
    return historical_data, df

@st.cache_data
def load_recent_purchases():
    data_dir = 'data'
    
    # Vérifier et télécharger les achats récents si nécessaire
    download_prepared_data()

    df_recent_purchases = pd.read_excel(os.path.join(data_dir, 'dataFR.xlsx'), engine='openpyxl')
    
    # Supprimer les lignes où la colonne 'Date' contient des valeurs non conformes
    df_recent_purchases = df_recent_purchases[pd.to_datetime(df_recent_purchases['Date'], errors='coerce').notnull()]

    if not pd.api.types.is_datetime64_any_dtype(df_recent_purchases['Date']):
        df_recent_purchases['Date'] = pd.to_datetime(df_recent_purchases['Date'], format='%Y-%m-%d', errors='coerce')
    
    return df_recent_purchases

@st.cache_data
def load_objectifs():
    data_dir = 'data'
    
    # Vérifier et télécharger les objectifs si nécessaire
    download_prepared_data()
    
    objectifs_df = pd.read_excel(os.path.join(data_dir, 'objectifs.xlsx'), engine='openpyxl')
    return objectifs_df

@st.cache_data
def load_segmentation_data():
    data_dir = 'data'
    
    # Vérifier et télécharger les données de segmentation si nécessaire
    download_prepared_data()
    
    segmentation_df = pd.read_excel(os.path.join(data_dir, 'segmentation_data.xlsx'), engine='openpyxl')
    return segmentation_df

def reassign_account_manager(df):
    df = df.sort_values(by=['Restaurant ID', 'Date de commande'])
    df['Owner email'] = df.groupby('Restaurant ID')['Owner email'].transform(lambda x: x.ffill().bfill())
    return df

def filter_data_by_account(df, account_manager):
    return df[df['Owner email'] == account_manager]

# Charger les données
historical_data, df = load_data()
df_recent_purchases = load_recent_purchases()
objectifs_df = load_objectifs()
segmentation_df = load_segmentation_data()
