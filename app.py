import streamlit as st
import pandas as pd
from src.data_processing import load_data, download_files
from src.calculations import process_country_data, calculate_segments_for_month
from src.plots import plot_ratios

# Fonction pour vider le cache
def clear_cache():
    st.caching.clear_cache()
    st.experimental_rerun()

# Télécharger et charger les données avec mise en cache
@st.cache(allow_output_mutation=True)
def get_data():
    download_files()
    return load_data()

# Interface utilisateur avec Streamlit
st.title('Analyse de la Rétention des Clients')

# Bouton pour mettre à jour les données
if st.button('Mettre à jour'):
    clear_cache()

historical_data, df = get_data()

country_code = st.selectbox('Sélectionner un pays', list(historical_data.keys()) + ['Global'])

if country_code == 'Global':
    all_historical_data = pd.concat(historical_data.values(), ignore_index=True)
    recent_months = pd.date_range(start='2024-05-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
    recent_results = pd.concat([calculate_segments_for_month(df, month) for month in recent_months], ignore_index=True)
    all_results = pd.concat([all_historical_data, recent_results], ignore_index=True)
else:
    all_results = process_country_data(df, historical_data, country_code)

june_2024_results = all_results[all_results['Mois'] == '2024-07']

st.header('Résumé des Segments pour Juillet 2024')
for segment in ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
    segment_data = june_2024_results[june_2024_results['Segment'] == segment].iloc[0]
    st.subheader(segment)
    st.write(f"Nombre de Clients: {segment_data['Nombre de Clients']}")
    st.write(f"Nombre de Clients Possible: {segment_data['Nombre de Clients Possible']}")
    st.write(f"Nombre de Clients Actifs (Mois Précédent): {segment_data['Nombre de Clients Actifs (Mois Précédent)']}")
    st.write(f"Rapport (%): {segment_data['Rapport (%)']}")

st.header('Graphiques des Segments')
for segment in ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
    fig = plot_ratios(segment, all_results, country_code)
    st.plotly_chart(fig)
