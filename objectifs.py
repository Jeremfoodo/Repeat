import streamlit as st
import pandas as pd
import sqlite3
from src.database import save_objectif, get_objectifs, update_objectif, init_db  # Assurez-vous que init_db est importé
from src.calculations import calculate_segments_for_month

# Initialize the database
init_db()

# Function to get the current number of active clients per segment and country
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

def objectifs_page(df):
    st.title('Définir les Objectifs de Clients Actifs pour Juillet 2024')

    # Interface pour entrer les objectifs
    countries = df['Pays'].unique()
    segments = ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']

    with st.form(key='objectifs_form'):
        st.write('Entrer les objectifs par segment et par pays')
        objectif_data = []
        for country in countries:
            for segment in segments:
                objectif = st.number_input(f'Objectif {segment} pour {country}', min_value=0, step=1)
                objectif_data.append((country, segment, objectif))

        code = st.text_input('Code de validation')
        submit_button = st.form_submit_button(label='Enregistrer les Objectifs')

        if submit_button:
            if code == 'Inesqueenofrepeat':
                for country, segment, objectif in objectif_data:
                    save_objectif(country, segment, objectif)
                st.success('Objectifs enregistrés avec succès!')
            else:
                st.error('Code de validation incorrect')

    # Afficher les objectifs actuels et les écarts par rapport aux clients actuels
    st.header('Objectifs Actuels et Écarts')
    objectifs = get_objectifs()
    st.write("Objectifs enregistrés:", objectifs)  # Ajout d'une impression pour vérifier la structure

    active_clients = get_active_clients(df, '2024-07')

    rows = []
    for objectif in objectifs:
        print(objectif)  # Ajout d'une impression pour vérifier la structure de chaque objectif
        pays, segment, obj = objectif  # Modifiez en fonction de la structure imprimée
        actuel = active_clients.get(pays, {}).get(segment, 0)
        ecart = obj - actuel
        rows.append({'Pays': pays, 'Segment': segment, 'Objectif': obj, 'Actuel': actuel, 'Écart': ecart})

    objectifs_df = pd.DataFrame(rows)
    st.dataframe(objectifs_df)

    # Bouton de téléchargement
    csv = objectifs_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Télécharger les objectifs en CSV",
        data=csv,
        file_name='objectifs_clients_actifs.csv',
        mime='text/csv',
    )

