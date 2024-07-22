import streamlit as st
import pandas as pd
from src.google_drive import download_excel_file
from src.calculations import calculate_segments_for_month

# URL du fichier Excel sur Google Drive
spreadsheet_url = "https://drive.google.com/uc?export=download&id=1UaAh3PUaHjBTShTYUGkd-Yw6fUT7TZJN"
output_file = "data/objectifs.xlsx"

# Télécharger le fichier Excel
download_excel_file(spreadsheet_url, output_file)

# Fonction pour obtenir les objectifs depuis le fichier Excel
def get_objectifs():
    objectifs_df = pd.read_excel(output_file, engine='openpyxl')
    return objectifs_df

# Fonction pour obtenir les clients actuels par segment et par pays
@st.cache_data
def get_active_clients(df, target_month):
    result = {}
    for country in df['Pays'].unique():
        country_df = df[df['Pays'] == country]
        active_clients = calculate_segments_for_month(country_df, target_month)
        result[country] = {
            'Nouveaux Clients': active_clients[active_clients['Segment'] == 'Nouveaux Clients']['Nombre de Clients'].values[0],
            'Clients Récents': active_clients[active_clients['Segment'] == 'Clients Récents']['Nombre de Clients'].values[0],
            'Anciens Clients': active_clients[active_clients['Segment'] == 'Anciens Clients']['Nombre de Clients'].values[0],
        }
    return result

# Fonction pour créer la page des objectifs
def objectifs_page(df):
    st.title('Objectifs de Clients Actifs pour Juillet 2024')

    # Récupérer les objectifs depuis le fichier Excel
    objectifs_df = get_objectifs()

    # Calculer les clients actuels pour juillet 2024
    active_clients = get_active_clients(df, '2024-07')

    # Préparer les données pour l'affichage
    rows = []
    for _, row in objectifs_df.iterrows():
        pays = row['country']
        segment = row['type']
        objectif = row['Nb clients']
        actuel = active_clients.get(pays, {}).get(segment, 0)
        ecart = objectif - actuel
        rows.append({'Pays': pays, 'Segment': segment, 'Objectif': objectif, 'Actuel': actuel, 'Écart': ecart})

    results_df = pd.DataFrame(rows)

    # Afficher le tableau
    st.header('Objectifs Actuels et Écarts')
    st.dataframe(results_df)

    # Bouton de téléchargement
    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Télécharger les objectifs en CSV",
        data=csv,
        file_name='objectifs_clients_actifs.csv',
        mime='text/csv',
    )

# Appel de la fonction pour créer la page des objectifs
if __name__ == "__main__":
    # Exemple de DataFrame df à passer à la fonction objectifs_page
    df = pd.read_csv('path/to/your/prepared_data.csv')
    objectifs_page(df)
