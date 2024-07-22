import streamlit as st
import pandas as pd
from src.data_processing import load_objectifs
from src.calculations import calculate_segments_for_month

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
    objectifs_df = load_objectifs()

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
