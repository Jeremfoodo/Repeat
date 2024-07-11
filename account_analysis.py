import streamlit as st
import pandas as pd
from src.data_processing import filter_data_by_account
from src.calculations import calculate_segments_for_month
from src.plots import plot_ratios
from global_analysis import generate_summary_boxes

@st.cache_data
def get_filtered_data(df, account_manager):
    return filter_data_by_account(df, account_manager)

@st.cache_data
def get_account_results(df_account, recent_months):
    return pd.concat([calculate_segments_for_month(df_account, month) for month in recent_months], ignore_index=True)

def account_analysis(df):
    st.title('Analyse de la Rétention par Account Manager')

    # Nettoyage de la colonne 'Owner email'
    df['Owner email'] = df['Owner email'].astype(str).dropna()

    # Sélection de l'account manager
    account_manager = st.selectbox(
        'Sélectionner un account manager',
        sorted(df['Owner email'].unique())
    )

    # Bouton pour mettre à jour les données
    if st.button('Mettre à jour'):
        st.cache_data.clear()
        st.experimental_rerun()

    # Filtrer les données par account manager
    df_account = get_filtered_data(df, account_manager)

    # Calculer les segments pour chaque mois depuis avril 2024 pour l'account manager
    recent_months = pd.date_range(start='2024-04-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
    account_results = get_account_results(df_account, recent_months)

    june_2024_results_account = account_results[account_results['Mois'] == '2024-07']

    st.header(f'Résumé des Segments pour Juillet 2024')
    st.subheader(f'<span style="font-size:14px; color:black; text-decoration:none;">{account_manager}</span>', unsafe_allow_html=True)
    summary_boxes_account = generate_summary_boxes(june_2024_results_account)

    # Afficher les boîtes dans une grille 2x2
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(summary_boxes_account[0], unsafe_allow_html=True)
        st.markdown(summary_boxes_account[1], unsafe_allow_html=True)
    with col2:
        st.markdown(summary_boxes_account[2], unsafe_allow_html=True)
        st.markdown(summary_boxes_account[3], unsafe_allow_html=True)

    st.header(f'Graphiques des Segments - {account_manager}')
    for segment in ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        fig = plot_ratios(segment, account_results, account_manager)
        st.plotly_chart(fig)
