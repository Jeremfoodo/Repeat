import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.data_processing import load_data
from src.calculations import get_clients_by_segment_and_spending, get_inactive_clients_july

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Générer les heatmaps pour juin et juillet 2024
    heatmap_data_june, total_clients_june, customer_spending_june = get_clients_by_segment_and_spending(df, '2024-06')
    heatmap_data_july, total_clients_july, customer_spending_july = get_clients_by_segment_and_spending(df, '2024-07')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Juin 2024')
        st.write(f"Nombre total de clients actifs: {total_clients_june}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_june.drop(columns='Total Clients').values,
            x=heatmap_data_june.columns[:-1],  # Exclude the 'Total Clients' column for heatmap
            y=heatmap_data_june.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_june.drop(columns='Total Clients').values,
            texttemplate="%{text}"
        ))

        # Ajouter une colonne de somme des clients
        for i, segment in enumerate(heatmap_data_june.index):
            fig.add_trace(go.Scatter(
                x=['Total Clients'],
                y=[segment],
                mode='text',
                text=[heatmap_data_june.loc[segment, 'Total Clients']],
                textfont=dict(color='black'),
                showlegend=False
            ))

        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col2:
        st.subheader('Juillet 2024')
        st.write(f"Nombre total de clients actifs: {total_clients_july}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_july.drop(columns='Total Clients').values,
            x=heatmap_data_july.columns[:-1],  # Exclude the 'Total Clients' column for heatmap
            y=heatmap_data_july.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_july.drop(columns='Total Clients').values,
            texttemplate="%{text}"
        ))

        # Ajouter une colonne de somme des clients
        for i, segment in enumerate(heatmap_data_july.index):
            fig.add_trace(go.Scatter(
                x=['Total Clients'],
                y=[segment],
                mode='text',
                text=[heatmap_data_july.loc[segment, 'Total Clients']],
                textfont=dict(color='black'),
                showlegend=False
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
    
    heatmap_data_june_account, total_clients_june_account, customer_spending_june_account = get_clients_by_segment_and_spending(df_account, '2024-06')
    heatmap_data_july_account, total_clients_july_account, customer_spending_july_account = get_clients_by_segment_and_spending(df_account, '2024-07')

    col3, col4 = st.columns(2)

    with col3:
        st.subheader(f'Juin 2024 - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_june_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_june_account.drop(columns='Total Clients').values,
            x=heatmap_data_june_account.columns[:-1],  # Exclude the 'Total Clients' column for heatmap
            y=heatmap_data_june_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_june_account.drop(columns='Total Clients').values,
            texttemplate="%{text}"
        ))

        # Ajouter une colonne de somme des clients
        for i, segment in enumerate(heatmap_data_june_account.index):
            fig.add_trace(go.Scatter(
                x=['Total Clients'],
                y=[segment],
                mode='text',
                text=[heatmap_data_june_account.loc[segment, 'Total Clients']],
                textfont=dict(color='black'),
                showlegend=False
            ))

        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col4:
        st.subheader(f'Juillet 2024 - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_july_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_july_account.drop(columns='Total Clients').values,
            x=heatmap_data_july_account.columns[:-1],  # Exclude the 'Total Clients' column for heatmap
            y=heatmap_data_july_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_july_account.drop(columns='Total Clients').values,
            texttemplate="%{text}"
        ))

        # Ajouter une colonne de somme des clients
        for i, segment in enumerate(heatmap_data_july_account.index):
            fig.add_trace(go.Scatter(
                x=['Total Clients'],
                y=[segment],
                mode='text',
                text=[heatmap_data_july_account.loc[segment, 'Total Clients']],
                textfont=dict(color='black'),
                showlegend=False
            ))

        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Vérification de la segmentation pour juin 2024
    st.subheader('Vérification de la segmentation pour juin 2024')
    st.write(customer_spending_june[['Restaurant ID', 'Restaurant', 'Total', 'Spending Level']])

    # Clients actifs en juin mais pas en juillet pour l'account manager sélectionné
    inactive_clients_account = get_inactive_clients_july(customer_spending_june_account, customer_spending_july_account)
    inactive_count_account = inactive_clients_account.shape[0]
    
    st.subheader(f'Clients actifs en juin mais inactifs en juillet pour {account_manager} ({inactive_count_account})')
    st.write(inactive_clients_account[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total']])
    
    # Option de téléchargement pour la liste des clients inactifs en juillet
    st.download_button(
        label='Télécharger la liste des clients inactifs en juillet',
        data=inactive_clients_account.to_csv(index=False),
        file_name=f'clients_inactifs_juillet_{account_manager}.csv',
        mime='text/csv'
    )

# Charger les données et afficher la page de segmentation
df = load_data()
segmentation_page(df)
