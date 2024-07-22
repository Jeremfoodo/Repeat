import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_processing import load_objectifs, load_data
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

    # Calculer les sous-totaux et les totaux
    sous_totaux = results_df.groupby('Pays').sum().reset_index()
    sous_totaux['Segment'] = 'Sous-total'
    
    total_general = results_df[['Objectif', 'Actuel', 'Écart']].sum()
    total_general['Pays'] = 'Total Général'
    total_general['Segment'] = ''
    total_general = pd.DataFrame(total_general).transpose()

    # Ajouter les sous-totaux et le total général au DataFrame des résultats
    results_df = pd.concat([results_df, sous_totaux, total_general], ignore_index=True)

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

    # Préparer les données pour le graphique en cascade
    waterfall_data = []
    for _, row in results_df.iterrows():
        if row['Pays'] != 'Total Général' and row['Segment'] != 'Sous-total':
            waterfall_data.append(dict(
                name=f"{row['Pays']} - {row['Segment']}",
                measure='relative',
                x=row['Pays'],
                y=row['Écart']
            ))

    waterfall_data.insert(0, dict(
        name='Objectif Total',
        measure='absolute',
        x='Objectif Total',
        y=total_general['Objectif'].values[0]
    ))

    waterfall_data.append(dict(
        name='Réalisé',
        measure='total',
        x='Réalisé',
        y=total_general['Actuel'].values[0]
    ))

    # Créer le graphique en cascade
    fig = go.Figure(go.Waterfall(
        measure=[d['measure'] for d in waterfall_data],
        x=[d['x'] for d in waterfall_data],
        textposition='outside',
        text=[d['y'] for d in waterfall_data],
        y=[d['y'] for d in waterfall_data]
    ))

    fig.update_layout(
        title="Objectif vs Réalisé",
        showlegend=True
    )

    # Afficher le graphique en cascade
    st.plotly_chart(fig)

# Appel de la fonction pour créer la page des objectifs
if __name__ == "__main__":
    # Charger les données
    historical_data, df = load_data()
    objectifs_page(df)
