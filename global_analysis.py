import streamlit as st
import pandas as pd
from src.calculations import process_country_data, calculate_segments_for_month, process_region_data
from src.plots import plot_ratios

def global_analysis_page(df):
    st.title("Analyse Globale")
    
def get_regions(country_code):
    if country_code == 'FR':
        return ['Paris', 'Paris EST', 'Paris Ouest', 'Province']
    elif country_code == 'US':
        return ['NY', 'CA']
    else:
        return []

def global_analysis(historical_data, df):
    st.title('Analyse de la Rétention des Clients')

    # Bouton pour mettre à jour les données
    if st.button('Mettre à jour'):
        st.cache_data.clear()
        st.experimental_rerun()

    countries = list(historical_data.keys()) + ['Global']
    country_code = st.selectbox('Sélectionner un pays ou une région', countries)

    if country_code == 'Global':
        all_historical_data = pd.concat(historical_data.values(), ignore_index=True)
        recent_months = pd.date_range(start='2024-05-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
        recent_results = pd.concat([calculate_segments_for_month(df, month) for month in recent_months], ignore_index=True)
        all_results = pd.concat([all_historical_data, recent_results], ignore_index=True)
    else:
        all_results = process_country_data(df, historical_data, country_code)
    
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
        fig = plot_ratios(segment, all_results, country_code)
        st.plotly_chart(fig)

    # Afficher l'analyse par région si FR ou US est sélectionné
    if country_code in ['FR', 'US']:
        st.header('Analyse par région')
        for region in get_regions(country_code):
            st.subheader(f'Région: {region}')
            try:
                region_results = process_region_data(df, country_code, region=region)
                region_june_2024_results = region_results[region_results['Mois'] == '2024-07']
                region_summary_boxes = generate_region_summary_boxes(region_june_2024_results)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(region_summary_boxes[0], unsafe_allow_html=True)
                    st.markdown(region_summary_boxes[1], unsafe_allow_html=True)
                with col2:
                    st.markdown(region_summary_boxes[2], unsafe_allow_html=True)
                    st.markdown(region_summary_boxes[3], unsafe_allow_html=True)
            except KeyError as e:
                st.error(f"Erreur: {e}")

def generate_summary_boxes(june_2024_results):
    colors = {
        'Acquisition': '#FFCCCC',
        'Nouveaux Clients': '#CCFFCC',
        'Clients Récents': '#CCCCFF',
        'Anciens Clients': '#FFCC99'
    }

    boxes = []
    for segment in ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        if segment in june_2024_results['Segment'].values:
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

def generate_region_summary_boxes(region_june_2024_results):
    colors = {
        'Acquisition': '#FFCCCC',
        'Nouveaux Clients': '#CCFFCC',
        'Clients Récents': '#CCCCFF',
        'Anciens Clients': '#FFCC99'
    }

    boxes = []
    for segment in ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        if segment in region_june_2024_results['Segment'].values:
            segment_data = region_june_2024_results[region_june_2024_results['Segment'] == segment].iloc[0]
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
