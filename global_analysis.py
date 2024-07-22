import streamlit as st
import pandas as pd
from src.calculations import process_country_data, calculate_segments_for_month
from src.plots import plot_ratios

def get_combined_regions(countries):
    combined = []
    for country in countries:
        combined.extend(get_regions(country))
    return combined

def get_regions(country_code):
    if country_code == 'FR':
        return ['FR', 'Paris', 'Paris EST', 'Paris Ouest', 'Province']
    elif country_code == 'US':
        return ['US', 'NY', 'CA']
    else:
        return [country_code]

def global_analysis(historical_data, df):
    st.title('Analyse de la Rétention des Clients')

    # Bouton pour mettre à jour les données
    if st.button('Mettre à jour'):
        st.cache_data.clear()
        st.experimental_rerun()

    countries = list(historical_data.keys())
    combined_regions = get_combined_regions(countries) + ['Global']
    selection = st.selectbox('Sélectionner un pays ou une région', combined_regions)

    if selection == 'Global':
        all_historical_data = pd.concat(historical_data.values(), ignore_index=True)
        recent_months = pd.date_range(start='2024-05-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
        recent_results = pd.concat([calculate_segments_for_month(df, month) for month in recent_months], ignore_index=True)
        all_results = pd.concat([all_historical_data, recent_results], ignore_index=True)
    else:
        if selection in get_regions('FR'):
            country_code = 'FR'
            region = selection if selection != 'FR' else None
        elif selection in get_regions('US'):
            country_code = 'US'
            region = selection if selection != 'US' else None
        else:
            country_code = selection
            region = None

        all_results = process_country_data(df, historical_data, country_code, region)

    june_2024_results = all_results[all_results['Mois'] == '2024-07']

    st.header('Résumé des Segments pour Juillet 2024')
    summary_boxes = generate_summary_boxes(june_2024_results)

    # Afficher les boîtes dans une grille 2x2
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(summary_boxes[0], unsafe_allow_html=True)
        st.markdown(summary_boxes[1], unsafe_allow_html=True)
    with col2:
        st.markdown(summary_boxes[2], unsafe_allow_html=True)
        st.markdown(summary_boxes[3], unsafe_allow_html=True)

    st.header('Graphiques des Segments')
    for segment in ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        fig = plot_ratios(segment, all_results, country_code if region is None else region)
        st.plotly_chart(fig)

def generate_summary_boxes(june_2024_results):
    colors = {
        'Acquisition': '#FFCCCC',
        'Nouveaux Clients': '#CCFFCC',
        'Clients Récents': '#CCCCFF',
        'Anciens Clients': '#FFCC99'
    }

    boxes = []
    for segment in ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        segment_data = june_2024_results[june_2024_results['Segment'] == segment].iloc[0]
        box = f"""
        <div style="background-color: {colors[segment]}; padding: 10px; margin: 10px; border-radius: 5px; width: 90%; height: 170px;">
            <h4 style="margin: 0; font-size: 16px;">{segment}</h4>
            <p style="margin: 2px 0; font-size: 14px;">Nombre de Clients: {segment_data['Nombre de Clients']}</p>
            <p style="margin: 2px 0; font-size: 14px;">Nombre de Clients Possible: {segment_data['Nombre de Clients Possible']}</p>
            <p style="margin: 2px 0; font-size: 14px;">Nombre de Clients Actifs (Mois Précédent): {segment_data['Nombre de Clients Actifs (Mois Précédent)']}</p>
            <p style="margin: 2px 0; font-size: 14px;">Rapport (%): {segment_data['Rapport (%)']}</p>
        </div>
        """
        boxes.append(box)
    return boxes
