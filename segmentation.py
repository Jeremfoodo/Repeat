import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
            z=heatmap_data_june.values,
            x=heatmap_data_june.columns,
            y=heatmap_data_june.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_june.values,
            texttemplate="%{text}"
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
            z=heatmap_data_july.values,
            x=heatmap_data_july.columns,
            y=heatmap_data_july.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_july.values,
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
    
    heatmap_data_june_account, total_clients_june_account, customer_spending_june_account = get_clients_by_segment_and_spending(df_account, '2024-06')
    heatmap_data_july_account, total_clients_july_account, customer_spending_july_account = get_clients_by_segment_and_spending(df_account, '2024-07')

    col3, col4 = st.columns(2)

    with col3:
        st.subheader(f'Juin 2024 - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_june_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_june_account.values,
            x=heatmap_data_june_account.columns,
            y=heatmap_data_june_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_june_account.values,
            texttemplate="%{text}"
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
            z=heatmap_data_july_account.values,
            x=heatmap_data_july_account.columns,
            y=heatmap_data_july_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_july_account.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Clients actifs en juin mais pas en juillet pour l'account manager sélectionné
    inactive_clients = get_inactive_clients_july(customer_spending_june_account, customer_spending_july_account)
    inactive_count = inactive_clients.shape[0]

    # Box rouge pour les clients inactifs en juillet
    st.markdown("<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🔴 Clients actifs en juin mais inactifs en juillet ({inactive_count})")
    st.markdown("<small>Ces clients n'ont pas refait d'achat en juillet, essayer un repeat ou comprendre les raisons du churn.</small>", unsafe_allow_html=True)
    st.dataframe(inactive_clients[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total']], height=300, style={"color": "white", "background-color": "red"})
    st.download_button(
        label='Télécharger la liste des clients inactifs en juillet',
        data=inactive_clients.to_csv(index=False),
        file_name='clients_inactifs_juillet.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients qui ont baissé dans le tiering
    downgraded_clients = customer_spending_june_account[customer_spending_june_account['Restaurant ID'].isin(customer_spending_july_account['Restaurant ID'])]
    downgraded_clients = downgraded_clients.merge(customer_spending_july_account, on='Restaurant ID', suffixes=('_Juin', '_Juillet'))
    downgraded_clients = downgraded_clients[downgraded_clients['Spending Level_Juin'] > downgraded_clients['Spending Level_Juillet']]
    downgraded_count = downgraded_clients.shape[0]

    # Box orange pour les clients qui ont baissé dans le tiering
    st.markdown("<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟠 Clients actifs en juillet mais qui ont baissé dans le tiering ({downgraded_count})")
    st.dataframe(downgraded_clients[['Restaurant ID', 'Restaurant_Juin', 'Spending Level_Juin', 'Total_Juin', 'Spending Level_Juillet', 'Total_Juillet']], height=300, style={"color": "white", "background-color": "orange"})
    st.markdown("</div>", unsafe_allow_html=True)

# Charger les données et afficher la page de segmentation
df = load_data()
segmentation_page(df)
