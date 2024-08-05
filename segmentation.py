import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.calculations import get_clients_by_segment_and_spending, get_inactive_clients, get_segment_and_spending_info

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Ajouter la colonne de la dernière commande pour chaque Restaurant ID
    df['Date de commande'] = pd.to_datetime(df['Date de commande'])
    last_order_dates = df.groupby('Restaurant ID')['Date de commande'].max().reset_index()
    last_order_dates.columns = ['Restaurant ID', 'Dernière commande']

    # Calculer les mois dynamiques
    today = datetime.today()
    current_month = today.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    current_month_str = current_month.strftime('%Y-%m')
    previous_month_str = previous_month.strftime('%Y-%m')

    # Générer les heatmaps pour les mois dynamiques
    heatmap_data_previous, total_clients_previous, customer_spending_previous = get_clients_by_segment_and_spending(df, previous_month_str)
    heatmap_data_current, total_clients_current, customer_spending_current = get_clients_by_segment_and_spending(df, current_month_str)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f'{previous_month.strftime("%B %Y")}')
        st.write(f"Nombre total de clients actifs: {total_clients_previous}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_previous.values,
            x=heatmap_data_previous.columns,
            y=heatmap_data_previous.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_previous.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col2:
        st.subheader(f'{current_month.strftime("%B %Y")}')
        st.write(f"Nombre total de clients actifs: {total_clients_current}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_current.values,
            x=heatmap_data_current.columns,
            y=heatmap_data_current.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_current.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Segmentation par account manager
    st.header('Segmentation par Account Manager')
    account_manager = st.selectbox('Sélectionner un account manager', df['Owner email'].unique())
    
    df_account = df[df['Owner email'] == account_manager]

    # Obtenir les informations de segmentation et de niveau de dépense pour les mois dynamiques
    customer_info_previous_account = get_segment_and_spending_info(df_account, previous_month_str)
    customer_info_current_account = get_segment_and_spending_info(df_account, current_month_str)

    # Fusionner les informations pour obtenir les colonnes nécessaires
    merged_previous_current = pd.merge(customer_info_previous_account, customer_info_current_account, on='Restaurant ID', suffixes=('_Previous', '_Current'), how='outer')
    merged_previous_current = pd.merge(merged_previous_current, last_order_dates, on='Restaurant ID', how='left')

    # Remplir les colonnes avec les valeurs appropriées
    merged_previous_current['Spending Level_Previous'] = merged_previous_current['Spending Level_Previous'].fillna('Unknown')
    merged_previous_current['Spending Level_Current'] = merged_previous_current['Spending Level_Current'].fillna('Unknown')
    merged_previous_current['Total_Previous'] = merged_previous_current['Total_Previous'].fillna(0)
    merged_previous_current['Total_Current'] = merged_previous_current['Total_Current'].fillna(0)
    merged_previous_current['Segment'] = merged_previous_current['Segment_Current'].fillna(merged_previous_current['Segment_Previous']).fillna('Unknown')

    # Séparer les clients dans les différents buckets
    inactive_clients = merged_previous_current[merged_previous_current['Total_Current'] == 0]
    downgraded_clients = merged_previous_current[(merged_previous_current['Spending Level_Previous'] != 'Unknown') & 
                                                 (merged_previous_current['Spending Level_Current'] != 'Unknown') & 
                                                 (merged_previous_current['Spending Level_Previous'] > merged_previous_current['Spending Level_Current'])]
    same_tier_less_spending_clients = merged_previous_current[(merged_previous_current['Spending Level_Previous'] == merged_previous_current['Spending Level_Current']) & 
                                                              (merged_previous_current['Total_Previous'] > merged_previous_current['Total_Current'])]
    increased_spending_clients = merged_previous_current[merged_previous_current['Total_Previous'] < merged_previous_current['Total_Current']]

    # Afficher les tables de clients
    def render_clients_table(clients, title):
        st.markdown(f"### {title}")
        st.dataframe(clients[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level_Previous', 'Spending Level_Current', 'Total_Previous', 'Total_Current', 'Dernière commande']])

    # Clients inactifs en juillet
    st.markdown("<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🔴 Clients actifs en {previous_month.strftime('%B %Y')} mais inactifs en {current_month.strftime('%B %Y')}")
    render_clients_table(inactive_clients, f"Clients inactifs en {current_month.strftime('%B %Y')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients qui ont baissé dans le tiering
    st.markdown("<div style='background-color: #fd7e14; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟠 Clients actifs en {current_month.strftime('%B %Y')} mais qui ont baissé dans le tiering")
    render_clients_table(downgraded_clients, "Clients qui ont baissé dans le tiering")
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé moins en juillet
    st.markdown("<div style='background-color: #ffebcc; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟡 Clients restés dans le même tiering mais dépensé moins en {current_month.strftime('%B %Y')}")
    render_clients_table(same_tier_less_spending_clients, "Clients restés dans le même tiering mais dépensé moins en juillet")
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé plus en juillet
    st.markdown("<div style='background-color: #d4edda; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟢 Clients qui ont augmenté leurs dépenses, bravo !")
    render_clients_table(increased_spending_clients, "Clients qui ont augmenté leurs dépenses")
    st.markdown("</div>", unsafe_allow_html=True)

# Appel de la fonction pour créer la page de segmentation
if __name__ == "__main__":
    # Charger le dataframe df
    df = pd.read_csv("votre_fichier.csv")
    segmentation_page(df)
