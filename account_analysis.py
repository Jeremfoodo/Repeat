import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.data_processing import filter_data_by_account
from src.calculations import calculate_segments_for_month
from src.plots import plot_ratios
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def account_analysis_page(df):
    st.title("Account Analysis")

@st.cache_data
def get_filtered_data(df, account_manager):
    return filter_data_by_account(df, account_manager)

@st.cache_data
def get_account_results(df_account, recent_months):
    return pd.concat([calculate_segments_for_month(df_account, month) for month in recent_months], ignore_index=True)

def generate_summary_boxes(results):
    colors = {
        'Acquisition': '#FFCCCC',
        'Nouveaux Clients': '#CCFFCC',
        'Clients Récents': '#CCCCFF',
        'Anciens Clients': '#FFCC99'
    }

    boxes = []
    for segment in ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        if segment in results['Segment'].values:
            segment_data = results[results['Segment'] == segment].iloc[0]
            box = f"""
            <div style="background-color: {colors[segment]}; padding: 5px; margin: 5px; border-radius: 5px; width: 90%; height: auto;">
                <h4 style="margin: 0; font-size: 14px; text-align: center;">{segment}</h4>
                <p style="margin: 2px 0; font-size: 12px;">Nombre de Clients: {segment_data['Nombre de Clients']}</p>
                <p style="margin: 2px 0; font-size: 12px;">Possible: {segment_data['Nombre de Clients Possible']}</p>
                <p style="margin: 2px 0; font-size: 12px;">Actifs (Mois Précédent): {segment_data['Nombre de Clients Actifs (Mois Précédent)']}</p>
                <p style="margin: 2px 0; font-size: 12px;">Rapport (%): {segment_data['Rapport (%)']}</p>
            </div>
            """
            boxes.append(box)
    return boxes

def account_analysis(df):
    st.title('Analyse de la Rétention par Account Manager')

    # Nettoyage de la colonne 'Owner email'
    df['Owner email'] = df['Owner email'].astype(str).dropna()

    # Disposition en colonnes pour la sélection et la mise à jour
    col1, col2 = st.columns([3, 1])
    with col1:
        account_manager = st.selectbox(
            'Sélectionner un account manager',
            sorted(df['Owner email'].unique())
        )
    with col2:
        if st.button('Mettre à jour'):
            st.cache_data.clear()
            st.experimental_rerun()

    # Filtrer les données par account manager
    df_account = get_filtered_data(df, account_manager)

    # Calculer les segments pour chaque mois depuis trois mois avant le mois en cours pour l'account manager
    today = datetime.today()
    current_month = today.replace(day=1)
    start_month = (current_month - pd.DateOffset(months=3)).strftime('%Y-%m')
    recent_months = pd.date_range(start=start_month, end=current_month, freq='MS').strftime('%Y-%m').tolist()
    account_results = get_account_results(df_account, recent_months)

    current_month_str = current_month.strftime('%Y-%m')
    current_month_results_account = account_results[account_results['Mois'] == current_month_str]

    st.header(f'Résumé des Segments pour {current_month_str}')
    st.markdown(f'<span style="font-size:14px; color:black; text-decoration:none;">{account_manager}</span>', unsafe_allow_html=True)
    summary_boxes_account = generate_summary_boxes(current_month_results_account)

    # Afficher les boîtes dans une grille 2x2 ou une seule rangée
    col1, col2, col3, col4 = st.columns(4)
    if len(summary_boxes_account) > 0:
        col1.markdown(summary_boxes_account[0], unsafe_allow_html=True)
    if len(summary_boxes_account) > 1:
        col2.markdown(summary_boxes_account[1], unsafe_allow_html=True)
    if len(summary_boxes_account) > 2:
        col3.markdown(summary_boxes_account[2], unsafe_allow_html=True)
    if len(summary_boxes_account) > 3:
        col4.markdown(summary_boxes_account[3], unsafe_allow_html=True)

    for segment in ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
        fig = plot_ratios(segment, account_results, account_manager)
        st.plotly_chart(fig, use_container_width=True)

    # Préparer le tableau
    df['Derniere commande'] = df.groupby('Restaurant ID')['Date de commande'].transform('max')
    df_latest = df[df['Owner email'] == account_manager].drop_duplicates('Restaurant ID')

    def client_type(row):
        first_order_month = row['date 1ere commande (Restaurant)'].strftime('%Y-%m')
        if first_order_month == current_month_str:
            return 'Acquisition'
        elif first_order_month == (current_month - pd.DateOffset(months=1)).strftime('%Y-%m'):
            return 'Nouveaux Clients'
        elif first_order_month in [(current_month - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]:
            return 'Clients Récents'
        else:
            return 'Anciens Clients'

    df_latest['Type de Client'] = df_latest.apply(client_type, axis=1)

    # Mise en forme des données pour le tableau
    df_display = df_latest[['Owner email', 'Restaurant ID', 'Restaurant', 'Type de Client', 'Derniere commande']]

    # Colorer les lignes en fonction de la date de dernière commande
    js = JsCode(f"""
    function(params) {{
        if (params.data['Derniere commande'].startsWith('{current_month_str}')) {{
            return {{
                'color': 'white',
                'backgroundColor': 'green'
            }}
        }} else {{
            return {{
                'color': 'white',
                'backgroundColor': 'red'
            }}
        }}
    }}
    """)

    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_columns(df_display.columns, filterable=True, sortable=True, resizable=True)
    gb.configure_column("Derniere commande", cellStyle=js)
    gb.configure_default_column(groupable=True)
    gb.configure_grid_options(domLayout='normal')

    grid_options = gb.build()

    AgGrid(df_display, gridOptions=grid_options, enable_enterprise_modules=True, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)

    # Bouton de téléchargement
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Télécharger les données en CSV",
        data=csv,
        file_name=f'{account_manager}_clients.csv',
        mime='text/csv',
    )

# Appel de la fonction pour créer la page des objectifs
if __name__ == "__main__":
    # Charger les données
    historical_data, df = load_data()
    account_analysis(df)
