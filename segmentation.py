import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    # Filtrer les commandes du mois cible
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    
    # Définir le niveau de dépense
    bins = [0, 500, 1500, 2000, float('inf')]
    labels = ['Basic', 'Silver', 'Gold', 'High Spenders']
    target_orders['Spending Level'] = pd.cut(target_orders.groupby('Restaurant ID')['Total'].transform('sum'), bins=bins, labels=labels)
    
    # Définir les segments
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    
    target_orders.loc[acquisition.index, 'Segment'] = 'Acquisition'
    target_orders.loc[nouveaux_clients.index, 'Segment'] = 'Nouveaux Clients'
    target_orders.loc[clients_recents.index, 'Segment'] = 'Clients Récents'
    target_orders.loc[anciens_clients.index, 'Segment'] = 'Anciens Clients'
    
    # Compter les clients et les dépenses totales par segment et niveau de dépense
    heatmap_data = target_orders.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique', 'Total': 'sum'}).reset_index()
    
    # Pivot pour obtenir le format désiré
    heatmap_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Restaurant ID').fillna(0)
    spending_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Total').fillna(0)
    
    return heatmap_pivot, spending_pivot

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays'] + df['Pays'].unique().tolist())
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Générer les heatmaps pour juin et juillet 2024
    heatmap_data_june, spending_data_june = get_clients_by_segment_and_spending(df, '2024-06')
    heatmap_data_july, spending_data_july = get_clients_by_segment_and_spending(df, '2024-07')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Juin 2024')
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_june.values,
            x=heatmap_data_june.columns,
            y=heatmap_data_june.index,
            colorscale='Viridis',
            hoverongaps=False,
            text=heatmap_data_june.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

        st.subheader('Total Dépenses - Juin 2024')
        fig_spending = go.Figure(data=go.Heatmap(
            z=spending_data_june.values,
            x=spending_data_june.columns,
            y=spending_data_june.index,
            colorscale='Viridis',
            hoverongaps=False,
            text=spending_data_june.values,
            texttemplate="%{text}"
        ))
        fig_spending.update_layout(
            title='Dépenses Totales par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig_spending)

    with col2:
        st.subheader('Juillet 2024')
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_july.values,
            x=heatmap_data_july.columns,
            y=heatmap_data_july.index,
            colorscale='Viridis',
            hoverongaps=False,
            text=heatmap_data_july.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

        st.subheader('Total Dépenses - Juillet 2024')
        fig_spending = go.Figure(data=go.Heatmap(
            z=spending_data_july.values,
            x=spending_data_july.columns,
            y=spending_data_july.index,
            colorscale='Viridis',
            hoverongaps=False,
            text=spending_data_july.values,
            texttemplate="%{text}"
        ))
        fig_spending.update_layout(
            title='Dépenses Totales par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig_spending)
